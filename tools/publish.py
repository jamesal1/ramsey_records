#!/usr/bin/env python3
"""
Add Ramsey lower-bound witnesses to this repository, or check that it is ready for a release.
See PUBLISHING.md for the full process.

  python tools/publish.py add --graph PATH --g-avoids J6 --complement-avoids J7 \\
      --base bases/VO_J5J7n64.g6 \\
      --previous 66 --previous-ref "[VO]" --upper 124 --upper-ref "[LidP]" \\
      --found 2026-11-18 --short "VO64 + 4 vertices by SAT" --method "..."

  python tools/publish.py claim K5e_K10e_n96 --g-avoids J5 --complement-avoids K10 \\
      --previous 92 --previous-source "..." --upper 233 --upper-ref "[BZ3]" \\
      --reason "K10 contains K10-e"     # another cell the same witness proves

  python tools/publish.py readme          # regenerate the README tables and the record pages
  python tools/publish.py release-check   # everything that must hold before tagging a release

`add` copies the graph into graphs/ (graph6 and 0/1 matrix), records SHA-256 hashes, the
exact difference from the base graph (if any), the connection set of an abelian Cayley graph
(if --cayley-group is given), nauty invariants when nauty is installed, and the output of
every available checker (verification/). It writes the record's page records/<id>.md: a
generated summary plus a "How it was found" section that is edited by hand afterwards. It
refuses a graph that any checker rejects, a graph checked by fewer than two independent
checkers, and a graph that does not beat the previous bound and every record already here in
that cell (unless --second-witness is given for an extra witness of an existing record).
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
    CHECKERS, ROOT, apply_diff, cayley_connection_set, checker_available, diff_from_base, encode_graph6,
    invariants, load_graph, load_records, matrix_text, parse_forbidden, rel, run_checker, save_records,
    sha256_file, survey_name,
)

SURVEY = "S. P. Radziszowski, Small Ramsey Numbers, Electron. J. Combin. DS1.18 (24 April 2026)"
README = os.path.join(ROOT, "README.md")
PAGES = os.path.join(ROOT, "records")
TABLE_START = "<!-- records-table:start -->"
TABLE_END = "<!-- records-table:end -->"
HEAD_START, HEAD_END = "<!-- generated:head -->", "<!-- /generated:head -->"
TAIL_START, TAIL_END = "<!-- generated:tail -->", "<!-- /generated:tail -->"


def short(spec):
    kind, s = parse_forbidden(spec)
    return f"K{s}e" if kind == "J" else f"K{s}"


def cell_name(a, b):
    return f"R({survey_name(a)}, {survey_name(b)})"


def rank(spec):
    kind, s = parse_forbidden(spec)
    return 2 * s - (1 if kind == "J" else 0)


def cell_key(claim):
    return (rank(claim["g_avoids"]), rank(claim["complement_avoids"]))


# --------------------------------------------------------------------------- #
# Claims: the primary cell of a record plus its also_proves entries
# --------------------------------------------------------------------------- #

def claims_of(rec):
    """Every cell this record proves, primary first, as dicts sharing the claim fields."""
    yield rec
    yield from rec.get("also_proves", [])


def all_claims(records):
    for r in records:
        for c in claims_of(r):
            yield r, c


def refresh_supersession(records):
    """A claim is superseded once a claim in the same cell with a higher bound exists. It is
    superseded by the earliest-found such claim (ties go to the smaller bound, the one that beat it first)."""
    by_cell = {}
    for r, c in all_claims(records):
        by_cell.setdefault(c["cell"], []).append((r, c))
    for entries in by_cell.values():
        for r, c in entries:
            higher = [(r2["found"], c2["lower_bound"], r2["id"]) for r2, c2 in entries
                      if c2["lower_bound"] > c["lower_bound"]]
            if higher:
                c["superseded_by"] = min(higher)[2]
            else:
                c.pop("superseded_by", None)


def best_in_cell(records, cell, exclude_id=None):
    vals = [c["lower_bound"] for r, c in all_claims(records) if c["cell"] == cell and r["id"] != exclude_id]
    return max(vals, default=None)


def bounds_args(args):
    """previous/upper fields from the command line."""
    if args.previous_source:
        prev_src = args.previous_source
    elif args.previous_ref:
        prev_src = f"{SURVEY}, Table {args.table}, lower bound {args.previous_ref}"
    else:
        sys.exit("give --previous-ref (a survey reference key) or --previous-source (free text)")
    out = {"previous_lower_bound": args.previous, "previous_source": prev_src,
           "upper_bound": args.upper, "upper_source": None}
    if args.upper is not None:
        if args.upper_source:
            out["upper_source"] = args.upper_source
        elif args.upper_ref:
            out["upper_source"] = f"{SURVEY}, Table {args.table}, upper bound {args.upper_ref}"
        else:
            sys.exit("give --upper-ref or --upper-source with --upper")
    return out


def run_all_checkers(names, g6_path, a, b, log_stem, prior=None):
    unknown = set(names) - set(CHECKERS)
    if unknown:
        sys.exit(f"unknown checkers: {sorted(unknown)}")
    available = [c for c in names if checker_available(c)]
    skipped = [c for c in names if c not in available]
    if len(available) + (1 if prior else 0) < 2:
        sys.exit(f"need at least two independent checkers (a --prior-verification counts as one), "
                 f"have {available} (unavailable: {skipped})")
    today = datetime.date.today().isoformat()
    os.makedirs(os.path.join(ROOT, "verification"), exist_ok=True)
    results, failed = [], False
    for c in available:
        status, out = run_checker(c, g6_path, a, b)
        log = os.path.join(ROOT, "verification", f"{log_stem}.{c}.txt")
        with open(log, "w") as f:
            f.write(f"# {today}  {CHECKERS[c][0]} {rel(g6_path)} {a} {b}\n{out}")
        print(f"  {c:9s} {status}  ({rel(log)})")
        results.append({"checker": CHECKERS[c][0], "result": status, "log": rel(log), "date": today})
        failed |= status != "VALID"
    return results, skipped, failed


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
    best = best_in_cell(records, cell)

    if args.second_witness:
        if best is None or bound != best:
            sys.exit(f"--second-witness needs an existing record for {cell} with bound {bound}")
    else:
        if bound <= args.previous:
            sys.exit(f"{cell}: graph proves >= {bound}, which does not beat the previous {args.previous}")
        if best is not None and bound <= best:
            sys.exit(f"{cell}: graph proves >= {bound}, but this repository already has >= {best} "
                     f"(use --second-witness to add another witness of an equal bound)")
    fields = bounds_args(args)

    base_id = f"{short(a)}_{short(b)}_n{n}"
    rid = base_id
    suffix = iter("bcdefghijklmnopqrstuvwxyz")
    while any(r["id"] == rid for r in records):
        rid = f"{base_id}_{next(suffix)}"

    structure = None
    if args.cayley_group:
        group = [int(x) for x in args.cayley_group.split(",")]
        S = cayley_connection_set(n, edges, group)
        if S is None:
            sys.exit(f"the graph is not the Cayley graph on Z_{' x Z_'.join(map(str, group))} in mixed-radix labels")
        structure = {"type": "abelian_cayley", "group": group, "connection_set": S}
    if args.structure:
        structure = {**(structure or {}), "description": args.structure}

    g6_path = os.path.join(ROOT, "graphs", rid + ".g6")
    mat_path = os.path.join(ROOT, "graphs", rid + ".txt")
    os.makedirs(os.path.dirname(g6_path), exist_ok=True)
    with open(g6_path, "w") as f:
        f.write(encode_graph6(n, edges) + "\n")
    with open(mat_path, "w") as f:
        f.write(matrix_text(n, edges))

    names = [c for c in args.checkers.split(",") if c]
    results, skipped, failed = run_all_checkers(names, g6_path, a, b, rid, args.prior_verification)
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
        **fields,
        "found": args.found,
        "method_short": args.short,
        "method": args.method,
        "page": f"records/{rid}.md",
    }
    if args.second_witness:
        rec["second_witness"] = True
    if structure:
        rec["structure"] = structure

    if args.base or args.base_record:
        deleted = [int(x) for x in args.base_deleted.split(",")] if args.base_deleted else []
        if args.base_record:
            src = next((r for r in records if r["id"] == args.base_record), None)
            if src is None:
                sys.exit(f"no record {args.base_record}")
            base_path = os.path.join(ROOT, src["files"]["graph6"]["path"])
            base_entry = {"base": rel(base_path), "base_sha256": src["files"]["graph6"]["sha256"],
                          "base_source": f"this repository, record {src['id']}"}
        else:
            base_entry = _base_entry(args)
            base_path = os.path.join(ROOT, base_entry["base"])
        bn, bedges = load_graph(base_path)
        diff = diff_from_base(n, edges, bn, bedges, deleted)
        if apply_diff(n, bedges, diff) != (n, edges):
            sys.exit("internal error: the diff does not rebuild the graph")
        rec["extends"] = {**base_entry, **diff}
        print(f"  base: {base_entry['base']}; {len(deleted)} base vertices deleted, "
              f"{len(diff['added_vertices'])} vertices added, "
              f"{len(diff['base_edges_removed'])} base edges removed, {len(diff['base_edges_added'])} added")

    rec["invariants"] = invariants(n, edges)
    rec["verification"] = results
    if args.prior_verification:
        rec["prior_verification"] = args.prior_verification
    if skipped:
        rec["verification_skipped"] = [CHECKERS[c][0] for c in skipped]

    records.append(rec)
    refresh_supersession(records)
    save_records(records)
    write_outputs(records)
    print(f"recorded {rid}: {cell} >= {bound} (previous: >= {args.previous}); page {rec['page']}")


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
# claim: another cell proved by an existing witness
# --------------------------------------------------------------------------- #

def cmd_claim(args):
    records = load_records()
    rec = next((r for r in records if r["id"] == args.id), None)
    if rec is None:
        sys.exit(f"no record {args.id}")
    a, b = args.g_avoids.upper(), args.complement_avoids.upper()
    cell = cell_name(a, b)
    if any(c["cell"] == cell for c in claims_of(rec)):
        sys.exit(f"{rec['id']} already claims {cell}")
    bound = rec["lower_bound"]
    best = best_in_cell(records, cell)
    if bound <= args.previous:
        sys.exit(f"{cell}: the witness proves >= {bound}, which does not beat the previous {args.previous}")
    if best is not None and bound <= best:
        sys.exit(f"{cell}: this repository already has >= {best}")
    fields = bounds_args(args)
    g6 = os.path.join(ROOT, rec["files"]["graph6"]["path"])
    names = [c for c in args.checkers.split(",") if c]
    results, skipped, failed = run_all_checkers(names, g6, a, b, f"{rec['id']}.{short(a)}_{short(b)}",
                                                args.prior_verification)
    if failed:
        sys.exit("a checker did not confirm the claim; nothing was recorded (logs kept in verification/)")
    claim = {"cell": cell, "g_avoids": a, "complement_avoids": b, "lower_bound": bound, **fields,
             "reason": args.reason, "verification": results}
    if args.prior_verification:
        claim["prior_verification"] = args.prior_verification
    if skipped:
        claim["verification_skipped"] = [CHECKERS[c][0] for c in skipped]
    rec.setdefault("also_proves", []).append(claim)
    refresh_supersession(records)
    save_records(records)
    write_outputs(records)
    print(f"recorded: {rec['id']} also proves {cell} >= {bound} (previous: >= {args.previous})")


# --------------------------------------------------------------------------- #
# README tables and record pages
# --------------------------------------------------------------------------- #

def bound_text(c):
    return f"{c['cell']} ≥ {c['lower_bound']}"


def upper_text(c):
    if c.get("upper_bound") is None:
        return "–"
    m = re.search(r"upper bound (\[[^\]]+\])", c.get("upper_source") or "")
    return f"{c['upper_bound']} {m.group(1)}" if m else str(c["upper_bound"])


def link(text, path, from_dir=""):
    target = os.path.relpath(os.path.join(ROOT, path), os.path.join(ROOT, from_dir)) if from_dir else path
    return f"[{text}]({target})"


def witness_link(rec, from_dir=""):
    p = rec["files"]["graph6"]["path"]
    return link(f"`{os.path.basename(p)}`", p, from_dir)


def write_readme_table(records):
    rows = sorted(all_claims(records), key=lambda rc: (cell_key(rc[1]), -rc[1]["lower_bound"], rc[0]["found"]))
    cur = ["| Bound | Before | Upper bound | Witness | How it was found | Found |",
           "|---|---|---|---|---|---|"]
    old = ["| Bound | Before | Witness | How it was found | Found | Superseded by |",
           "|---|---|---|---|---|---|"]
    ids = {r["id"]: r for r in records}
    for r, c in rows:
        how = link(r["method_short"], r["page"])
        b = f"**{bound_text(c)}**"
        if r.get("second_witness") and c is r:
            b += " (second witness)"
        if "superseded_by" in c:
            sup = ids[c["superseded_by"]]
            sc = next(x for x in claims_of(sup) if x["cell"] == c["cell"])
            sup_link = link("≥ %d" % sc["lower_bound"], sup["page"])
            old.append(f"| {bound_text(c)} | {c['previous_lower_bound']} | {witness_link(r)} | {how} | {r['found']} "
                       f"| {sup_link} |")
        else:
            cur.append(f"| {b} | {c['previous_lower_bound']} | {upper_text(c)} | {witness_link(r)} | {how} "
                       f"| {r['found']} |")
    table = "\n".join(cur)
    if len(old) > 2:
        table += ("\n\nEarlier records, since superseded. Each page says how the graph was found and what "
                  "replaced it.\n\n" + "\n".join(old))
    text = open(README).read()
    if TABLE_START not in text or TABLE_END not in text:
        sys.exit(f"README.md is missing the {TABLE_START} / {TABLE_END} markers")
    pre, rest = text.split(TABLE_START, 1)
    _, post = rest.split(TABLE_END, 1)
    with open(README, "w") as f:
        f.write(f"{pre}{TABLE_START}\n{table}\n{TABLE_END}{post}")


def group_name(group):
    return " × ".join(f"Z{m}" for m in group)


def page_head(rec, records):
    ids = {r["id"]: r for r in records}
    d = "records"
    title = " and ".join(f"{c['cell']} ≥ {c['lower_bound']}" for c in claims_of(rec))
    lines = [f"# {title}", "",
             f"[All records](../README.md) · witness {witness_link(rec, d)} "
             f"(graph6) · {link('adjacency matrix', rec['files']['matrix']['path'], d)}", "",
             "| Bound | Before | Upper bound | Status |", "|---|---|---|---|"]
    notes = []
    for i, c in enumerate(claims_of(rec), 1):
        if "superseded_by" in c:
            sup = ids[c["superseded_by"]]
            sc = next(x for x in claims_of(sup) if x["cell"] == c["cell"])
            status = "superseded by " + link("≥ %d" % sc["lower_bound"], sup["page"], d)
        else:
            status = "current record" if not (c is rec and rec.get("second_witness")) else "second witness"
        lines.append(f"| {c['cell']} ≥ **{c['lower_bound']}** | {c['previous_lower_bound']} ({i}) "
                     f"| {upper_text(c)} | {status} |")
        why = f" {c['reason']}" if c.get("reason") else ""
        notes.append(f"{i}. {c['cell']}: before, {c['previous_lower_bound']} ({c['previous_source']}).{why}")
    a = survey_name(rec["g_avoids"])
    b = survey_name(rec["complement_avoids"])
    lines += ["", *notes, "",
              f"The witness is a {rec['vertices']}-vertex graph with no {a} whose complement has no {b}. "
              f"Found {rec['found']}."]
    return "\n".join(lines)


def page_tail(rec):
    d = "records"
    inv = rec.get("invariants", {})
    deg = (f"{inv['min_degree']}-regular" if inv.get("min_degree") == inv.get("max_degree")
           else f"degrees {inv.get('min_degree')}–{inv.get('max_degree')}")
    facts = [f"{rec['vertices']} vertices, {rec['edges']} edges, {deg}"]
    if "automorphism_group_size" in inv:
        facts[0] += f"; automorphism group of order {inv['automorphism_group_size']} (nauty)"
    lines = ["## The graph", "", f"- {facts[0]}."]
    st = rec.get("structure") or {}
    if st.get("type") == "abelian_cayley":
        g = st["group"]
        k = len(st["connection_set"])
        if len(g) == 1:
            S = ", ".join(str(s[0]) for s in st["connection_set"])
            lines.append(f"- Circulant (Cayley graph on Z{g[0]}): vertices are the residues mod {g[0]}, and v ~ w "
                         f"exactly when w − v mod {g[0]} is in the connection set S ({k} elements). "
                         f"`verify.py` rebuilds the graph from S.")
        else:
            coords = ", ".join(f"a{i + 1}" for i in range(len(g)))
            radix = "a1"
            for i, m in enumerate(g[1:]):
                radix = f"({radix}) · {m} + a{i + 2}" if i else f"{radix} · {m} + a{i + 2}"
            S = ", ".join("(" + ", ".join(map(str, s)) + ")" for s in st["connection_set"])
            lines.append(f"- Cayley graph on {group_name(g)}: vertex v is the element ({coords}) with "
                         f"v = {radix}, and v ~ w exactly when w − v is in the connection set S "
                         f"({k} elements). `verify.py` rebuilds the graph from S.")
        lines += ["", "  S = {" + S + "}"]
    if st.get("description"):
        lines.append(f"- {st['description']}")
    ext = rec.get("extends")
    if ext:
        k = ext["base_vertices"] - len(ext.get("base_vertices_deleted", []))
        base = link(f"`{os.path.basename(ext['base'])}`", ext["base"], d)
        src = ext["base_source"]
        src = f"[source]({src})" if src.startswith("http") else src
        dels = ext.get("base_vertices_deleted")
        if dels:
            s = (f"- Vertices 0–{k - 1} are the base graph {base} ({src}) with its vertices "
                 f"{', '.join(map(str, dels))} deleted and the rest kept in order")
        else:
            s = f"- Vertices 0–{k - 1} are the base graph {base} ({src}), same labelling"
        changed = len(ext["base_edges_removed"]) + len(ext["base_edges_added"])
        s += ("; every edge among them is unchanged" if not changed else
              f"; {len(ext['base_edges_removed'])} base edges removed and {len(ext['base_edges_added'])} added")
        s += (f". Vertices {k}–{rec['vertices'] - 1} are new; their neighbourhoods are in `records.json` "
              f"(`extends.added_vertices`), and `verify.py` rebuilds the graph from the base and that list.")
        lines.append(s)
    lines += ["", "## Checks", "", "| Claim | Checker | Result | Log |", "|---|---|---|---|"]
    for c in claims_of(rec):
        for v in c["verification"]:
            lines.append(f"| {c['cell']} ≥ {c['lower_bound']} | `{v['checker']}` | {v['result']} "
                         f"| {link(os.path.basename(v['log']), v['log'], d)} |")
        if c.get("prior_verification"):
            lines.append(f"| {c['cell']} ≥ {c['lower_bound']} | before publication | VALID | {c['prior_verification']} |")
    g6 = rec["files"]["graph6"]["path"]
    lines += ["", "```bash", "cc -O2 -o check checkers/check.c"]
    for c in claims_of(rec):
        lines.append(f"./check {g6} {c['g_avoids']} {c['complement_avoids']}")
    lines += ["```", "", f"SHA-256 of `{os.path.basename(g6)}`: `{rec['files']['graph6']['sha256']}`"]
    return "\n".join(lines)


def replace_block(text, start, end, body):
    if start in text and end in text:
        pre, rest = text.split(start, 1)
        _, post = rest.split(end, 1)
        return f"{pre}{start}\n{body}\n{end}{post}"
    return None


def write_page(rec, records):
    path = os.path.join(ROOT, rec["page"])
    head, tail = page_head(rec, records), page_tail(rec)
    if os.path.exists(path):
        text = open(path).read()
        text = replace_block(text, HEAD_START, HEAD_END, head)
        text = text and replace_block(text, TAIL_START, TAIL_END, tail)
        if text is None:
            sys.exit(f"{rec['page']} is missing its generated-block markers")
    else:
        text = (f"{HEAD_START}\n{head}\n{HEAD_END}\n\n## How it was found\n\n{rec['method']}\n\n"
                f"{TAIL_START}\n{tail}\n{TAIL_END}\n")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def write_outputs(records):
    write_readme_table(records)
    for r in records:
        write_page(r, records)


def cmd_add_checker(args):
    """Run one more checker on existing records (every claimed cell) and record its result and log."""
    if args.checker not in CHECKERS:
        sys.exit(f"unknown checker {args.checker!r}")
    if not checker_available(args.checker):
        sys.exit(f"checker {args.checker!r} is not available on this machine")
    records = load_records()
    name = CHECKERS[args.checker][0]
    today = datetime.date.today().isoformat()
    failed = False
    for r in records:
        if args.ids and r["id"] not in args.ids:
            continue
        g6 = os.path.join(ROOT, r["files"]["graph6"]["path"])
        for c in claims_of(r):
            stem = r["id"] if c is r else f"{r['id']}.{short(c['g_avoids'])}_{short(c['complement_avoids'])}"
            status, out = run_checker(args.checker, g6, c["g_avoids"], c["complement_avoids"])
            log = os.path.join(ROOT, "verification", f"{stem}.{args.checker}.txt")
            with open(log, "w") as f:
                f.write(f"# {today}  {name} {rel(g6)} {c['g_avoids']} {c['complement_avoids']}\n{out}")
            print(f"  {r['id']:16s} {c['cell']:18s} {status}")
            c["verification"] = [v for v in c["verification"] if v["checker"] != name]
            c["verification"].append({"checker": name, "result": status, "log": rel(log), "date": today})
            skipped = [x for x in c.get("verification_skipped", []) if x != name]
            if skipped:
                c["verification_skipped"] = skipped
            else:
                c.pop("verification_skipped", None)
            failed |= status != "VALID"
    save_records(records)
    write_outputs(records)
    if failed:
        sys.exit(f"{name} did NOT confirm every record; see verification/")


def cmd_readme(_args):
    records = load_records()
    refresh_supersession(records)
    save_records(records)
    write_outputs(records)
    print("README.md tables and records/*.md pages regenerated")


# --------------------------------------------------------------------------- #
# release-check
# --------------------------------------------------------------------------- #

def cmd_release_check(_args):
    problems = []
    for name in ("CITATION.cff", ".zenodo.json", "README.md"):
        text = open(os.path.join(ROOT, name)).read()
        if "TODO" in text:
            problems.append(f"{name} still contains TODO placeholders")
    for r in load_records():
        page = os.path.join(ROOT, r.get("page", ""))
        if not r.get("page") or not os.path.exists(page):
            problems.append(f"{r['id']} has no page")
        elif "TODO" in open(page).read():
            problems.append(f"{r['page']} still contains TODO placeholders")
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


def add_bounds_options(p):
    p.add_argument("--previous", type=int, required=True, help="best lower bound known before this record")
    p.add_argument("--previous-ref", help='survey reference key for the previous bound, e.g. "[VO]"')
    p.add_argument("--previous-source", help="free-text source of the previous bound (overrides --previous-ref)")
    p.add_argument("--upper", type=int, help="survey upper bound (omit if none is printed)")
    p.add_argument("--upper-ref", help='survey reference key, e.g. "[LidP]"')
    p.add_argument("--upper-source", help="free-text source of the upper bound (overrides --upper-ref)")
    p.add_argument("--table", default="IIIa", help="survey table (default IIIa)")
    p.add_argument("--checkers", default="c,networkx,sage", help="comma list from: " + ",".join(CHECKERS))
    p.add_argument("--prior-verification", help="an independent check the graph already passed before it came here "
                   "(e.g. where and with what); counts as one of the two required checkers")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add", help="add a witness graph")
    p.add_argument("--graph", required=True, help="graph6 or 0/1 matrix file")
    p.add_argument("--g-avoids", required=True, help="what G avoids, e.g. J6 (= K6-e) or K8")
    p.add_argument("--complement-avoids", required=True, help="what the complement avoids, e.g. J7")
    add_bounds_options(p)
    p.add_argument("--found", required=True, help="date found, YYYY-MM-DD")
    p.add_argument("--short", required=True, help="a few words for the README table, e.g. 'Cayley graph on Z4 x Z4 x Z5'")
    p.add_argument("--method", required=True, help="first draft of the page's 'How it was found' section")
    p.add_argument("--base", help="published graph this one extends")
    p.add_argument("--base-record", help="id of a record in this repository that this graph extends")
    p.add_argument("--base-deleted", help="comma list of base vertices deleted (the rest keep their order)")
    p.add_argument("--base-name", help="file name to store the base under in bases/")
    p.add_argument("--base-source", help="where the base graph was published (URL)")
    p.add_argument("--cayley-group", help="abelian group as moduli, e.g. 16,2,7: store and check the connection set")
    p.add_argument("--structure", help="one sentence on the graph's structure for its page")
    p.add_argument("--second-witness", action="store_true", help="another witness for an existing bound")
    p.set_defaults(func=cmd_add)
    p = sub.add_parser("claim", help="record another cell an existing witness proves")
    p.add_argument("id", help="record id")
    p.add_argument("--g-avoids", required=True)
    p.add_argument("--complement-avoids", required=True)
    add_bounds_options(p)
    p.add_argument("--reason", required=True, help="why the witness proves this cell, e.g. 'K10 contains K10-e'")
    p.set_defaults(func=cmd_claim)
    p = sub.add_parser("add-checker", help="run another checker on existing records and record it")
    p.add_argument("checker", help="one of: " + ",".join(CHECKERS))
    p.add_argument("ids", nargs="*", help="record ids (default: all)")
    p.set_defaults(func=cmd_add_checker)
    sub.add_parser("readme", help="regenerate the README tables and record pages").set_defaults(func=cmd_readme)
    sub.add_parser("release-check", help="check the repository is ready to tag").set_defaults(func=cmd_release_check)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
