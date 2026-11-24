# Publishing process

The steps from a candidate graph to a citable, time-stamped record. Steps 1–4 are local and
can be repeated freely. Step 5 onwards makes things public.

## 1. Check the candidate beats the literature

- Look up the cell in the current revision of Radziszowski's survey
  (https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS1). Note the lower and
  upper bound and their reference keys.
- Search for anything newer: arXiv, Van Overberghe's circulant-Ramsey repository, and other
  record repositories (e.g. google-research/ramsey_number_bounds).
- Remember the implications between cells. Avoiding K_s − e implies avoiding K_s, and
  K_s − e contains K_{s−1}, so a graph may also prove something in a neighbouring cell. Check
  every cell the graph touches before deciding which to claim.

## 2. Add the record

```bash
python tools/publish.py add \
  --graph /path/to/candidate.g6 --g-avoids J6 --complement-avoids J7 \
  --base bases/VO_J5J7n64.g6 \
  --previous 66 --previous-ref "[VO]" --upper 124 --upper-ref "[LidP]" \
  --found 2026-11-18 --short "VO64 + 4 vertices by SAT" \
  --method "Exact SAT extension of ... by 4 vertices; ..."
```

This tool:
- refuses a graph that does not beat both the previous bound and any record already here in that
  cell (use `--second-witness` to add another graph for an existing bound);
- runs the checkers given by `--checkers` (default C, NetworkX and Sage when `sage -python` works or
  `RAMSEY_SAGE_PYTHON` points at a Python with Sage). It refuses unless at least two independent
  checks passed and none failed. A graph already checked independently before it came here (for
  example with NetworkX or Sage in the search repository) can be added with `--checkers c
  --prior-verification "checked with ... when found (date)"`; the prior check counts as one;
- writes `graphs/<id>.g6` and `graphs/<id>.txt`, their SHA-256 hashes, nauty invariants (canonical
  form, automorphism group size) when nauty is installed, and how to rebuild the graph:
  - `--base FILE` (a published graph) or `--base-record ID` (a record here): the exact difference
    from the base. If some base vertices were deleted, give them with `--base-deleted 21,47`; the
    remaining base vertices must keep their order as vertices 0, 1, ...;
  - `--cayley-group 16,2,7`: checks that the graph is the Cayley graph on Z16 × Z2 × Z7 in
    mixed-radix labels and stores the connection set; `--structure TEXT` adds a sentence for other
    structure (for example a non-abelian Cayley graph);
- saves the checker outputs to `verification/`, recomputes which records are superseded, regenerates
  the tables in `README.md`, and writes the record's page `records/<id>.md`.

The previous bound is the best one known without our graphs: `--previous-ref` for the survey's own
value, or `--previous-source "..."` for anything else (a derivation from published results, or a
result newer than the survey). `--upper` is optional for cells with no printed upper bound.

Then write the page. Its "How it was found" section starts as the `--method` text; rewrite it by
hand: the seed, the search, how long it took, what was tried and failed around it, and anything it
supersedes. Everything between the `generated` markers is rewritten by `publish.py readme`; the rest
of the page is left alone.

If the same graph proves another cell (for example K10 contains K10 − e, so a graph whose
complement has no K10 − e also has no K10), record that with

```bash
python tools/publish.py claim K5e_K10e_n96 --g-avoids J5 --complement-avoids K10 \
  --previous 92 --previous-source "R(4,10) >= 92 (DS1.18 Table I [HaKr1])" \
  --upper 233 --upper-ref "[BZ3]" --reason "K10 contains K10-e." --checkers c,networkx
```

A new base graph needs `--base-source URL` once. It is copied into `bases/` and its hash is
pinned in `bases/sources.json`.

To add a checker's result to existing records later (for example Sage, run on another
machine), run `python tools/publish.py add-checker sage` there, then copy `records.json`,
`README.md`, `records/` and the new `verification/*.sage.txt` files back. Sage installs cleanly from
conda-forge on Linux (`conda create -n sage -c conda-forge sage`). It needs the environment's
`bin` on `PATH` (it starts a `gap` binary), so set
`PATH=$HOME/miniconda3/envs/sage/bin:$PATH` and
`RAMSEY_SAGE_PYTHON=$HOME/miniconda3/envs/sage/bin/python`.

## 3. Verify from scratch

```bash
python verify.py --checkers c,networkx,sage
```

This rechecks every hash, confirms that the graph6 and matrix files agree, rebuilds each graph
from its base plus the recorded diff or from its Cayley connection set, and reruns the checkers on
every cell each record claims. NetworkX is impractical on the largest graphs; leave it out there. Also run it from a fresh clone
on a second machine if possible.

## 4. Commit

Review `git diff`, then commit the graphs, `records.json`, `records/`, `verification/` and
`README.md` together, one commit per batch of records.

## 5. Release (time stamp and DOI)

One-time setup:
- Make the GitHub repository public.
- Sign in to https://zenodo.org with GitHub, open *GitHub* in the account menu, and switch on
  this repository. Zenodo then archives every GitHub release and mints a DOI for it, using
  `.zenodo.json` for the metadata.

For each release:
1. Bump `version` in both `CITATION.cff` and `.zenodo.json`, and set `date-released`.
2. `python tools/publish.py release-check`. It fails on TODO placeholders, mismatched
   versions, a failing `verify.py`, or uncommitted changes.
3. Push, then create the GitHub release with tag `v<version>`
   (`gh release create v1.0.0 --title "v1.0.0" --notes "..."`). The release, not the push,
   triggers Zenodo.
4. Copy the DOI that Zenodo shows into `README.md` (badge and "How to cite") and into
   `CITATION.cff` (`doi:`), and commit. That commit goes into the next release.

The GitHub release and the Zenodo record are both dated, and either one establishes priority.

## 6. Tell people

- Email Stanisław Radziszowski (survey maintainer) with the cells, the new bounds, and the
  DOI, so the next survey revision can include them.
- Tell Steven Van Overberghe, since every witness extends his graph.
- Optionally, open a pull request to any record-tracking repository that covers these cells.

## Rules

- Never edit or delete a published graph file. A correction is a new record; the old one gets
  `superseded_by` or a note.
- Every record states which graph it extends and exactly how it differs, or gives its structure.
- Every record has a page saying how it was found. Superseded records stay, with their pages, and
  are listed under "Earlier records".
- Post superseded records only when they came from a different approach; one ladder's intermediate
  graphs are not separate records.
- A claim needs at least two independent checkers, and their logs are kept in `verification/`.
