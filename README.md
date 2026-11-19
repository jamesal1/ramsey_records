# New lower bounds for Ramsey numbers R(K_k − e, K_l − e) and R(K_k − e, K_l)

Explicit graphs that improve lower bounds listed in Table IIIa of Radziszowski's dynamic survey
*Small Ramsey Numbers* (Electron. J. Combin. DS1.18, 24 April 2026).

A graph G on n vertices with no A in G and no B in its complement proves R(A, B) ≥ n + 1.
Here K_k − e is the complete graph on k vertices minus one edge.

<!-- records-table:start -->
| Cell | Survey bounds | New lower bound | Witness | n | Found | Checked by |
|---|---|---|---|---|---|---|
| R(K5-e, K8) | 69 – 117 | **71** | [`K5e_K8_n70.g6`](graphs/K5e_K8_n70.g6) | 70 | 2026-11-19 | check.c, check_networkx.py |
| R(K5-e, K8-e) | 66 – 91 | **67** | [`K5e_K8e_n66.g6`](graphs/K5e_K8e_n66.g6) | 66 | 2026-11-19 | check.c, check_networkx.py |
| R(K5-e, K9-e) | 69 – 136 | **72** | [`K5e_K9e_n71.g6`](graphs/K5e_K9e_n71.g6) | 71 | 2026-11-19 | check.c, check_networkx.py |
| R(K6-e, K7-e) | 66 – 124 | **69** | [`K6e_K7e_n68.g6`](graphs/K6e_K7e_n68.g6) | 68 | 2026-11-18 | check.c, check_networkx.py |
| R(K6-e, K7-e) | 66 – 124 | 69 (second witness) | [`K6e_K7e_n68_b.g6`](graphs/K6e_K7e_n68_b.g6) | 68 | 2026-11-19 | check.c, check_networkx.py |
<!-- records-table:end -->

"Survey bounds" are the lower and upper bounds in Table IIIa. Superseded witnesses stay in
`records.json`, marked `superseded_by`.

## How they were found

Every graph here extends Steven Van Overberghe's 64-vertex graph `J5J7n64.g6`, the graph that
proves R(K5 − e, K7 − e) = 65 ([circulant-Ramsey](https://github.com/Steven-VO/circulant-Ramsey),
`RamseyGraphs/Jn/`). Vertices 0–63 of each witness are that graph, with its labelling and every
edge unchanged. The new vertices and their neighbourhoods were found by an exact SAT search
(CaDiCaL through PySAT, cube-and-conquer with lexicographic symmetry breaking).

So each record is fully described by the base graph plus the neighbourhoods of the new
vertices. `records.json` lists them in `extends.added_vertices`: for each new vertex v, its
neighbours with index below v, so an edge between two new vertices appears once, under the
later vertex. `verify.py` rebuilds every graph from the base and that list.

## Check them yourself

```bash
cc -O2 -o check checkers/check.c
./check graphs/K6e_K7e_n68.g6 J6 J7
```

Arguments are the graph file, what G must avoid and what its complement must avoid
(`J6` = K6 − e, `K8` = K8). Each check takes well under a second.

To verify every record (hashes, files, diffs from the base graph, and two checkers):

```bash
pip install networkx
python verify.py
python verify.py --checkers c,networkx,sage   # also Sage, if installed
```

Three independent checkers are provided. Each one uses a different test for K_s − e:

| Checker | K_s | K_s − e |
|---|---|---|
| `checkers/check.c` | bitset clique search | an (s−2)-clique with two common neighbours |
| `checkers/check_networkx.py` | NetworkX clique enumeration | two (s−1)-cliques sharing s−2 vertices |
| `checkers/check_sage.py` | Sage `clique_number` (Cliquer) | Sage `subgraph_search(..., induced=False)` |

Every witness a checker reports is re-verified by counting edges. The outputs from when each
record was added are in `verification/`.

## Files

- `graphs/`: each witness as a graph6 string (`.g6`) and as an n × n 0/1 adjacency matrix (`.txt`).
- `bases/`: the published graphs the witnesses extend; `bases/sources.json` gives their sources and hashes.
- `records.json`: one entry per witness: the cell, bounds before and after, SHA-256 of both files,
  the exact difference from the base graph, nauty invariants, and the checker results.
- `verification/`: checker output for each record.
- `checkers/`: the three checkers.
- `verify.py`: re-checks everything.
- `tools/publish.py`, `PUBLISHING.md`: how records are added and released.

## How to cite

See `CITATION.cff`. A Zenodo DOI is minted for each GitHub release.

## Licence

Apache License 2.0 (see `LICENSE`).
