"""Shared helpers for tools/publish.py and verify.py. Standard library only."""

import json
import os
import shlex
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "checkers"))
from graph_io import (  # noqa: E402,F401
    decode_graph6, encode_graph6, load_graph, matrix_text, parse_forbidden, sha256_file, survey_name,
)

RECORDS = os.path.join(ROOT, "records.json")
BUILD = os.path.join(ROOT, "build")


def rel(path):
    return os.path.relpath(path, ROOT)


def load_records():
    if not os.path.exists(RECORDS):
        return []
    with open(RECORDS) as f:
        return json.load(f)


def save_records(records):
    records.sort(key=lambda r: (r["cell"], -r["lower_bound"], r["id"]))
    with open(RECORDS, "w") as f:
        json.dump(records, f, indent=2)
        f.write("\n")


# --------------------------------------------------------------------------- #
# Checkers
# --------------------------------------------------------------------------- #

def _c_binary():
    src = os.path.join(ROOT, "checkers", "check.c")
    exe = os.path.join(BUILD, "check")
    if not os.path.exists(exe) or os.path.getmtime(exe) < os.path.getmtime(src):
        os.makedirs(BUILD, exist_ok=True)
        cc = os.environ.get("CC", "cc")
        subprocess.run([cc, "-O2", "-o", exe, src], check=True)
    return [exe]


def _sage_cmd():
    cmd = os.environ.get("RAMSEY_SAGE_PYTHON", "sage -python")
    return shlex.split(cmd)


CHECKERS = {
    # name: (description, function returning the command prefix)
    "c": ("checkers/check.c", _c_binary),
    "networkx": ("checkers/check_networkx.py", lambda: [sys.executable, os.path.join(ROOT, "checkers", "check_networkx.py")]),
    "sage": ("checkers/check_sage.py", lambda: _sage_cmd() + [os.path.join(ROOT, "checkers", "check_sage.py")]),
}


def checker_available(name):
    if name == "c":
        return shutil.which(os.environ.get("CC", "cc")) is not None
    if name == "networkx":
        try:
            import networkx  # noqa: F401
            return True
        except ImportError:
            return False
    if name == "sage":
        try:
            r = subprocess.run(_sage_cmd() + ["-c", "import sage.all"], capture_output=True, timeout=300)
            return r.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False
    return False


def run_checker(name, graph_path, g_avoids, c_avoids, timeout=None):
    """Run one checker. Returns (status, output) with status 'VALID', 'INVALID' or 'ERROR'."""
    cmd = CHECKERS[name][1]() + [rel(graph_path), g_avoids, c_avoids]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "ERROR", f"timed out after {timeout} s"
    out = r.stdout + (("\n[stderr]\n" + r.stderr) if r.stderr.strip() else "")
    if r.returncode == 0 and "result: VALID" in r.stdout:
        return "VALID", out
    if r.returncode == 1 and "result: INVALID" in r.stdout:
        return "INVALID", out
    return "ERROR", out


# --------------------------------------------------------------------------- #
# Diffs against a base graph
# --------------------------------------------------------------------------- #

def diff_from_base(n, edges, base_n, base_edges):
    """Describe a graph as base graph (on vertices 0..base_n-1, same labelling) plus changes."""
    if n < base_n:
        raise ValueError("graph is smaller than its base")
    eset = set(edges)
    inside = {e for e in eset if e[1] < base_n}
    bset = set(base_edges)
    nbrs = {v: [] for v in range(base_n, n)}
    for i, j in sorted(eset - inside):
        nbrs[j].append(i)  # j >= base_n always; i may be a base or a new vertex
    return {
        "base_vertices": base_n,
        "base_edges_removed": [list(e) for e in sorted(bset - inside)],
        "base_edges_added": [list(e) for e in sorted(inside - bset)],
        "added_vertices": {str(v): sorted(nb) for v, nb in nbrs.items()},
    }


def apply_diff(n, base_edges, diff):
    """Rebuild the edge list from a base graph and a diff (inverse of diff_from_base)."""
    eset = set(map(tuple, base_edges))
    eset -= {tuple(e) for e in diff["base_edges_removed"]}
    eset |= {tuple(e) for e in diff["base_edges_added"]}
    for v, nb in diff["added_vertices"].items():
        for u in nb:
            eset.add((min(u, int(v)), max(u, int(v))))
    return n, sorted(eset)


# --------------------------------------------------------------------------- #
# Invariants
# --------------------------------------------------------------------------- #

def invariants(n, edges):
    deg = [0] * n
    for i, j in edges:
        deg[i] += 1
        deg[j] += 1
    inv = {"min_degree": min(deg), "max_degree": max(deg)}
    g6 = encode_graph6(n, edges)
    if shutil.which("labelg"):
        r = subprocess.run(["labelg", "-q"], input=g6 + "\n", capture_output=True, text=True)
        if r.returncode == 0:
            inv["canonical_graph6_nauty"] = r.stdout.strip()
    if shutil.which("countg"):
        r = subprocess.run(["countg", "--a"], input=g6 + "\n", capture_output=True, text=True)
        for tok in r.stdout.replace(";", " ").split():
            if tok.startswith("groupsize="):
                inv["automorphism_group_size"] = int(float(tok.split("=")[1]))
    return inv
