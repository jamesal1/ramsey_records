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
  --found 2026-11-18 \
  --method "Exact SAT extension of ... by 4 vertices; ..."
```

This tool:
- refuses a graph that does not beat both the survey bound and any record already here
  (use `--second-witness` to add another graph for an existing bound);
- runs every available checker (C and NetworkX, plus Sage when `sage -python` works or
  `RAMSEY_SAGE_PYTHON` points at a Python with Sage). It refuses unless at least two
  independent checkers ran and all of them accept the graph;
- writes `graphs/<id>.g6` and `graphs/<id>.txt`, their SHA-256 hashes, the exact difference
  from the base graph (removed and added base edges, and the neighbourhood of every new
  vertex), and nauty invariants (canonical form, automorphism group size) when nauty is installed;
- saves the checker outputs to `verification/`, marks older records in the cell
  `superseded_by`, and regenerates the table in `README.md`.

A new base graph needs `--base-source URL` once. It is copied into `bases/` and its hash is
pinned in `bases/sources.json`.

## 3. Verify from scratch

```bash
python verify.py --checkers c,networkx,sage
```

This rechecks every hash, confirms that the graph6 and matrix files agree, rebuilds each graph
from its base plus the recorded diff, and reruns the checkers. Also run it from a fresh clone
on a second machine if possible.

## 4. Commit

Review `git diff`, then commit the graphs, `records.json`, `verification/` and `README.md`
together, one commit per batch of records.

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
- Every record states which published graph it extends and exactly how it differs.
- A claim needs at least two independent checkers, and their logs are kept in `verification/`.
