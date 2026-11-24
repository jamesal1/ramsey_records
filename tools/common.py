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

def diff_from_base(n, edges, base_n, base_edges, deleted=()):
    """Describe a graph as base graph plus changes.

    The base graph's vertices, minus `deleted`, keep their order and become vertices
    0..k-1 of the graph (k = base_n - len(deleted)); vertices k..n-1 are new.
    """
    deleted = sorted(set(deleted))
    keep = [v for v in range(base_n) if v not in set(deleted)]
    k = len(keep)
    if n < k:
        raise ValueError("graph is smaller than its base")
    pos = {v: i for i, v in enumerate(keep)}
    eset = set(edges)
    inside = {e for e in eset if e[1] < k}
    bset = {(pos[i], pos[j]) for i, j in base_edges if i in pos and j in pos}
    inv = {i: v for v, i in pos.items()}
    nbrs = {v: [] for v in range(k, n)}
    for i, j in sorted(eset - inside):
        nbrs[j].append(i)  # j >= k always; i may be a base or a new vertex
    diff = {"base_vertices": base_n}
    if deleted:
        diff["base_vertices_deleted"] = deleted
    # base edges are named by their labels in the base graph
    diff["base_edges_removed"] = [[inv[i], inv[j]] for i, j in sorted(bset - inside)]
    diff["base_edges_added"] = [[inv[i], inv[j]] for i, j in sorted(inside - bset)]
    diff["added_vertices"] = {str(v): sorted(nb) for v, nb in nbrs.items()}
    return diff


def apply_diff(n, base_edges, diff):
    """Rebuild the edge list from a base graph and a diff (inverse of diff_from_base)."""
    deleted = set(diff.get("base_vertices_deleted", []))
    keep = [v for v in range(diff["base_vertices"]) if v not in deleted]
    pos = {v: i for i, v in enumerate(keep)}
    eset = {tuple(e) for e in map(tuple, base_edges)}
    eset -= {tuple(e) for e in diff["base_edges_removed"]}
    eset |= {tuple(e) for e in diff["base_edges_added"]}
    out = {(pos[i], pos[j]) for i, j in eset if i in pos and j in pos}
    for v, nb in diff["added_vertices"].items():
        for u in nb:
            out.add((min(u, int(v)), max(u, int(v))))
    return n, sorted(out)


# --------------------------------------------------------------------------- #
# Abelian Cayley graphs
# --------------------------------------------------------------------------- #

def _radix(group):
    def dec(v):
        t = []
        for m in reversed(group):
            t.append(v % m)
            v //= m
        return tuple(reversed(t))

    def enc(t):
        v = 0
        for x, m in zip(t, group):
            v = v * m + x
        return v
    return dec, enc


def cayley_edges(group, connection_set):
    """Edges of the Cayley graph on Z_{m1} x ... x Z_{mr}; vertex v is the element whose
    mixed-radix digits (most significant first) are v's coordinates."""
    dec, enc = _radix(group)
    n = 1
    for m in group:
        n *= m
    S = [tuple(s) for s in connection_set]
    edges = set()
    for v in range(n):
        a = dec(v)
        for s in S:
            w = enc(tuple((x + y) % m for x, y, m in zip(a, s, group)))
            if w != v:
                edges.add((min(v, w), max(v, w)))
    return n, sorted(edges)


def cayley_connection_set(n, edges, group):
    """The connection set if (n, edges) is the Cayley graph on `group` in mixed-radix labels, else None."""
    dec, _ = _radix(group)
    nbrs0 = sorted({j for i, j in edges if i == 0} | {i for i, j in edges if j == 0})
    S = [list(dec(v)) for v in nbrs0]
    if cayley_edges(group, S) != (n, sorted(edges)):
        return None
    return S


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
