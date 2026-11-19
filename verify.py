#!/usr/bin/env python3
"""
Verify every record in records.json from scratch.

For each record this checks that:
  1. the graph files exist and match their SHA-256 hashes;
  2. the graph6 file and the 0/1 matrix describe the same graph, with the stated vertex and
     edge counts, and lower_bound = vertices + 1;
  3. if the record extends a published base graph: the base matches its hash, and applying the
     recorded diff to the base rebuilds the graph exactly;
  4. every selected checker reports the graph valid (G avoids g_avoids, complement avoids
     complement_avoids).

Usage:
  python verify.py                       # checkers c and networkx
  python verify.py --checkers c,networkx,sage
  python verify.py --no-checkers         # hashes, files and diffs only
Exit status 0 if everything holds, 1 otherwise.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))
from common import (  # noqa: E402
    CHECKERS, ROOT, apply_diff, checker_available, decode_graph6, load_graph, load_records, run_checker,
    sha256_file,
)


def check_record(rec, checkers):
    errors = []
    path = lambda p: os.path.join(ROOT, p)  # noqa: E731

    for kind, f in rec["files"].items():
        if not os.path.exists(path(f["path"])):
            errors.append(f"missing {f['path']}")
        elif sha256_file(path(f["path"])) != f["sha256"]:
            errors.append(f"sha256 mismatch for {f['path']}")
    if errors:
        return errors

    g6 = load_graph(path(rec["files"]["graph6"]["path"]))
    mat = load_graph(path(rec["files"]["matrix"]["path"]))
    if g6 != mat:
        errors.append("graph6 and matrix files describe different graphs")
    n, edges = g6
    if n != rec["vertices"] or len(edges) != rec["edges"]:
        errors.append(f"file has n={n}, e={len(edges)}; record says n={rec['vertices']}, e={rec['edges']}")
    if rec["lower_bound"] != n + 1:
        errors.append(f"lower_bound {rec['lower_bound']} != vertices + 1")

    ext = rec.get("extends")
    if ext:
        if sha256_file(path(ext["base"])) != ext["base_sha256"]:
            errors.append(f"base {ext['base']} does not match its sha256")
        else:
            bn, bedges = load_graph(path(ext["base"]))
            if bn != ext["base_vertices"]:
                errors.append("base vertex count differs from record")
            elif apply_diff(n, bedges, ext) != (n, edges):
                errors.append("base + recorded diff does not rebuild the graph")

    for c in checkers:
        status, out = run_checker(c, path(rec["files"]["graph6"]["path"]), rec["g_avoids"], rec["complement_avoids"])
        print(f"    {c:9s} {status}")
        if status != "VALID":
            errors.append(f"{c}: {status}\n{out}")
    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--checkers", default="c,networkx", help="comma list from: " + ",".join(CHECKERS))
    ap.add_argument("--no-checkers", action="store_true", help="skip the Ramsey checks")
    args = ap.parse_args()

    checkers = [] if args.no_checkers else [c for c in args.checkers.split(",") if c]
    for c in checkers:
        if c not in CHECKERS:
            sys.exit(f"unknown checker {c!r}")
        if not checker_available(c):
            sys.exit(f"checker {c!r} is not available on this machine")

    records = load_records()
    failures = 0
    for rec in records:
        tag = " (superseded)" if "superseded_by" in rec else ""
        print(f"{rec['id']}: {rec['cell']} >= {rec['lower_bound']}{tag}")
        errs = check_record(rec, checkers)
        if errs:
            failures += 1
            for e in errs:
                print(f"    FAIL {e}")
        else:
            print("    ok")
    print(f"\n{len(records) - failures}/{len(records)} records verified"
          + (f" with {', '.join(checkers)}" if checkers else " (no checkers run)"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
