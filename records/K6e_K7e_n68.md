<!-- generated:head -->
# R(K6-e, K7-e) ≥ 69

[All records](../README.md) · witness [`K6e_K7e_n68.g6`](../graphs/K6e_K7e_n68.g6) (graph6) · [adjacency matrix](../graphs/K6e_K7e_n68.txt)

| Bound | Before | Upper bound | Status |
|---|---|---|---|
| R(K6-e, K7-e) ≥ **69** | 66 (1) | 124 [LidP] | superseded by [≥ 70](K6e_K7e_n69.md) |

1. R(K6-e, K7-e): before, 66 (S. P. Radziszowski, Small Ramsey Numbers, Electron. J. Combin. DS1.18 (24 April 2026), Table IIIa, lower bound [VO]).

The witness is a 68-vertex graph with no K6-e whose complement has no K7-e. Found 2026-11-18.
<!-- /generated:head -->

## How it was found

The first record here. Starting from Van Overberghe's 64-vertex (K5-e, K7-e)-graph `J5J7n64` (VO64), the graph that proves R(K5-e, K7-e) = 65, an exact SAT search (CaDiCaL through PySAT, cube-and-conquer with lexicographic symmetry breaking) looked for new vertices whose neighbourhoods keep the graph free of K6-e and its complement free of K7-e. VO64 + 2, + 3 and + 4 vertices all exist (66, 67 and 68 vertices); the 68-vertex graph here adds 4 pairwise non-adjacent vertices. Adding a 5th to the 67- and 68-vertex graphs, or swapping one vertex for two, was UNSAT.

Superseded two days later by [the 69-vertex graph](K6e_K7e_n69.md), which came from a larger delete-and-add step on a different 68-vertex VO64 + 4 graph.

<!-- generated:tail -->
## The graph

- 68 vertices, 1020 edges, degrees 28–40; automorphism group of order 1 (nauty).
- Vertices 0–63 are the base graph [`VO_J5J7n64.g6`](../bases/VO_J5J7n64.g6) ([source](https://github.com/Steven-VO/circulant-Ramsey/blob/master/RamseyGraphs/Jn/J5J7n64.g6)), same labelling; every edge among them is unchanged. Vertices 64–67 are new; their neighbourhoods are in `records.json` (`extends.added_vertices`), and `verify.py` rebuilds the graph from the base and that list.

## Checks

| Claim | Checker | Result | Log |
|---|---|---|---|
| R(K6-e, K7-e) ≥ 69 | `checkers/check.c` | VALID | [K6e_K7e_n68.c.txt](../verification/K6e_K7e_n68.c.txt) |
| R(K6-e, K7-e) ≥ 69 | `checkers/check_networkx.py` | VALID | [K6e_K7e_n68.networkx.txt](../verification/K6e_K7e_n68.networkx.txt) |
| R(K6-e, K7-e) ≥ 69 | `checkers/check_sage.py` | VALID | [K6e_K7e_n68.sage.txt](../verification/K6e_K7e_n68.sage.txt) |

```bash
cc -O2 -o check checkers/check.c
./check graphs/K6e_K7e_n68.g6 J6 J7
```

SHA-256 of `K6e_K7e_n68.g6`: `86f3681bf440c6e7b222c7b8b757ff0d91c479c0dc7e4f6133df1bab1e3e4f5b`
<!-- /generated:tail -->
