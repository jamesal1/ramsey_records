#!/usr/bin/env python3
"""
Add a Ramsey lower-bound witness to this repository, or check that the repository is ready
for a release. See PUBLISHING.md for the full process.

  python tools/publish.py add --graph PATH --g-avoids J6 --complement-avoids J7 \\
      --base bases/VO_J5J7n64.g6 \\
      --previous 66 --previous-ref "[VO]" --upper 124 --upper-ref "[LidP]" \\
      --found 2026-11-18 --method "..."

  python tools/publish.py readme          # regenerate the table in README.md
  python tools/publish.py release-check   # everything that must hold before tagging a release

`add` copies the graph into graphs/ (graph6 and 0/1 matrix), records SHA-256 hashes, the
exact difference from the base graph, nauty invariants when nauty is installed, and the output
of every available checker (verification/). It refuses a graph that any checker rejects, a
graph checked by fewer than two independent checkers, and a graph that does not beat the
survey bound (unless --second-witness is given for an extra witness of an existing record).
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (  # noqa: E402
    CHECKERS, ROOT, apply_diff, checker_available, diff_from_base, encode_graph6, invariants, load_graph,
    load_records, matrix_text, parse_forbidden, rel, run_checker, save_records, sha256_file, survey_name,
)

SURVEY = "S. P. Radziszowski, Small Ramsey Numbers, Electron. J. Combin. DS1.18 (24 April 2026)"
README = os.path.join(ROOT, "README.md")
TABLE_START = "<!-- records-table:start -->"
TABLE_END = "<!-- records-table:end -->"


def short(spec):
    kind, s = parse_forbidden(spec)
    return f"K{s}e" if kind == "J" else f"K{s}"


def cell_name(a, b):
    return f"R({survey_name(a)}, {survey_name(b)})"


# --------------------------------------------------------------------------- #
# add
# --------------------------------------------------------------------------- #

def cmd_add(args):
    records = load_records()
    a, b = args.g_avoids.upper(), args.complement_avoids.upper()
    parse_forbidden(a), parse_forbidden(b)
    n, edges = load_graph(args.graph)
    bound = n + 1
    cell = cell_name(a, b)
    same_cell = [r for r in records if r["cell"] == cell and "superseded_by" not in r]
    best = max((r["lower_bound"] for r in same_cell), default=None)

    if args.second_witness:
        if best is None or bound != best:
            sys.exit(f"--second-witness needs an existing record for {cell} with bound {bound}")
    else:
        if bound <= args.previous:
            sys.exit(f"{cell}: graph proves >= {bound}, which does not beat the survey's {args.previous}")
        if best is not None and bound <= best:
            sys.exit(f"{cell}: graph proves >= {bound}, but this repository already has >= {best} "
                     f"(use --second-witness to add another witness of an equal bound)")

    # ---- run the checkers before writing anything --------------------------
    names = [c for c in args.checkers.split(",") if c]
    unknown = set(names) - set(CHECKERS)
    if unknown:
        sys.exit(f"unknown checkers: {sorted(unknown)}")
    available = [c for c in names if checker_available(c)]
    skipped = [c for c in names if c not in available]
    if len(available) < 2:
        sys.exit(f"need at least two independent checkers, have {available} (unavailable: {skipped})")

    base_id = f"{short(a)}_{short(b)}_n{n}"
    rid = base_id
    suffix = iter("bcdefghijklmnopqrstuvwxyz")
    while any(r["id"] == rid for r in records):
        rid = f"{base_id}_{next(suffix)}"

    g6_path = os.path.join(ROOT, "graphs", rid + ".g6")
    mat_path = os.path.join(ROOT, "graphs", rid + ".txt")
    os.makedirs(os.path.dirname(g6_path), exist_ok=True)
    with open(g6_path, "w") as f:
        f.write(encode_graph6(n, edges) + "\n")
    with open(mat_path, "w") as f:
        f.write(matrix_text(n, edges))

    results = []
    today = datetime.date.today().isoformat()
    os.makedirs(os.path.join(ROOT, "verification"), exist_ok=True)
    failed = False
    for c in available:
        status, out = run_checker(c, g6_path, a, b)
        log = os.path.join(ROOT, "verification", f"{rid}.{c}.txt")
        with open(log, "w") as f:
            f.write(f"# {today}  {CHECKERS[c][0]} {rel(g6_path)} {a} {b}\n{out}")
        print(f"  {c:9s} {status}  ({rel(log)})")
        results.append({"checker": CHECKERS[c][0], "result": status, "log": rel(log), "date": today})
        failed |= status != "VALID"
    if failed:
        for p in (g6_path, mat_path):
            os.remove(p)
        sys.exit("a checker did not confirm the graph; nothing was recorded (logs kept in verification/)")

    rec = {
        "id": rid,
        "cell": cell,
        "g_avoids": a,
        "complement_avoids": b,
        "lower_bound": bound,
        "vertices": n,
        "edges": len(edges),
        "files": {
            "graph6": {"path": rel(g6_path), "sha256": sha256_file(g6_path)},
            "matrix": {"path": rel(mat_path), "sha256": sha256_file(mat_path)},
        },
        "previous_lower_bound": args.previous,
        "previous_source": f"{SURVEY}, Table {args.table}, lower bound {args.previous_ref}",
        "upper_bound": args.upper,
        "upper_source": f"{SURVEY}, Table {args.table}, upper bound {args.upper_ref}",
        "found": args.found,
        "method": args.method,
    }
    if args.second_witness:
        rec["second_witness"] = True

    if args.base:
        bn, bedges = load_graph(args.base)
        diff = diff_from_base(n, edges, bn, bedges)
        if apply_diff(n, bedges, diff) != (n, edges):
            sys.exit("internal error: the diff does not rebuild the graph")
        base_entry = _base_entry(args)
        rec["extends"] = {**base_entry, **diff}
        print(f"  base: {base_entry['base']}; {len(diff['added_vertices'])} vertices added, "
              f"{len(diff['base_edges_removed'])} base edges removed, {len(diff['base_edges_added'])} added")

    rec["invariants"] = invariants(n, edges)
    rec["verification"] = results
    if skipped:
        rec["verification_skipped"] = [CHECKERS[c][0] for c in skipped]

    if not args.second_witness:
        for r in same_cell:
            r["superseded_by"] = rid
    records.append(rec)
    save_records(records)
    write_readme_table(records)
    print(f"recorded {rid}: {cell} >= {bound} (survey: >= {args.previous})")


def _base_entry(args):
    """Copy the base graph into bases/ if needed and describe it."""
    src = os.path.abspath(args.base)
    bases_dir = os.path.join(ROOT, "bases")
    if os.path.dirname(src) != bases_dir:
        os.makedirs(bases_dir, exist_ok=True)
        dst = os.path.join(bases_dir, args.base_name or os.path.basename(src))
        if os.path.exists(dst) and sha256_file(dst) != sha256_file(src):
            sys.exit(f"{rel(dst)} exists with different contents")
        with open(src) as f, open(dst, "w") as g:
            g.write(f.read())
        src = dst
    meta_path = os.path.join(bases_dir, "sources.json")
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    entry = meta.get(rel(src))
    if entry is None:
        if not args.base_source:
            sys.exit(f"new base {rel(src)}: give --base-source (where it was published)")
        entry = {"source": args.base_source, "sha256": sha256_file(src)}
        meta[rel(src)] = entry
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)
            f.write("\n")
    if entry["sha256"] != sha256_file(src):
        sys.exit(f"{rel(src)} does not match the hash in bases/sources.json")
    return {"base": rel(src), "base_sha256": entry["sha256"], "base_source": entry["source"]}


# --------------------------------------------------------------------------- #
# README table
# --------------------------------------------------------------------------- #

def write_readme_table(records):
    rows = ["| Cell | Survey bounds | New lower bound | Witness | n | Found | Checked by |",
            "|---|---|---|---|---|---|---|"]
    for r in records:
        if "superseded_by" in r:
            continue
        checked = ", ".join(v["checker"].split("/")[-1] for v in r["verification"] if v["result"] == "VALID")
        witness = f"[`{os.path.basename(r['files']['graph6']['path'])}`]({r['files']['graph6']['path']})"
        new = f"**{r['lower_bound']}**" if not r.get("second_witness") else f"{r['lower_bound']} (second witness)"
        rows.append(f"| {r['cell']} | {r['previous_lower_bound']} – {r['upper_bound']} | {new} | {witness} "
                    f"| {r['vertices']} | {r['found']} | {checked} |")
    table = "\n".join(rows)
    text = open(README).read()
    if TABLE_START not in text or TABLE_END not in text:
        sys.exit(f"README.md is missing the {TABLE_START} / {TABLE_END} markers")
    pre, rest = text.split(TABLE_START, 1)
    _, post = rest.split(TABLE_END, 1)
    with open(README, "w") as f:
        f.write(f"{pre}{TABLE_START}\n{table}\n{TABLE_END}{post}")


def cmd_readme(_args):
    write_readme_table(load_records())
    print("README.md table regenerated")


# --------------------------------------------------------------------------- #
# release-check
# --------------------------------------------------------------------------- #

def cmd_release_check(_args):
    problems = []
    for name in ("CITATION.cff", ".zenodo.json", "README.md"):
        text = open(os.path.join(ROOT, name)).read()
        if "TODO" in text:
            problems.append(f"{name} still contains TODO placeholders")
    cff = open(os.path.join(ROOT, "CITATION.cff")).read()
    zen = json.load(open(os.path.join(ROOT, ".zenodo.json")))
    m = re.search(r'^version:\s*"?([^"\n]+)"?', cff, re.M)
    if not m or m.group(1).strip() != zen.get("version"):
        problems.append("CITATION.cff and .zenodo.json versions differ")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "verify.py")], cwd=ROOT)
    if r.returncode != 0:
        problems.append("verify.py failed")
    st = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout
    if st.strip():
        problems.append("working tree is not clean:\n" + st)
    if problems:
        print("NOT READY:\n- " + "\n- ".join(problems))
        sys.exit(1)
    print(f"ready to release version {zen.get('version')}: git tag v{zen.get('version')} && git push --tags")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add", help="add a witness graph")
    p.add_argument("--graph", required=True, help="graph6 or 0/1 matrix file")
    p.add_argument("--g-avoids", required=True, help="what G avoids, e.g. J6 (= K6-e) or K8")
    p.add_argument("--complement-avoids", required=True, help="what the complement avoids, e.g. J7")
    p.add_argument("--previous", type=int, required=True, help="survey lower bound")
    p.add_argument("--previous-ref", required=True, help='survey reference key, e.g. "[VO]"')
    p.add_argument("--upper", type=int, required=True, help="survey upper bound")
    p.add_argument("--upper-ref", required=True, help='survey reference key, e.g. "[LidP]"')
    p.add_argument("--table", default="IIIa", help="survey table (default IIIa)")
    p.add_argument("--found", required=True, help="date found, YYYY-MM-DD")
    p.add_argument("--method", required=True, help="one-paragraph description of how it was found")
    p.add_argument("--base", help="published graph this one extends (vertices 0..m-1, same labelling)")
    p.add_argument("--base-name", help="file name to store the base under in bases/")
    p.add_argument("--base-source", help="where the base graph was published (URL)")
    p.add_argument("--checkers", default="c,networkx,sage", help="comma list from: " + ",".join(CHECKERS))
    p.add_argument("--second-witness", action="store_true", help="another witness for an existing bound")
    p.set_defaults(func=cmd_add)
    sub.add_parser("readme", help="regenerate the README table").set_defaults(func=cmd_readme)
    sub.add_parser("release-check", help="check the repository is ready to tag").set_defaults(func=cmd_release_check)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
