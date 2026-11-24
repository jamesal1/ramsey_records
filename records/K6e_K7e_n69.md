<!-- generated:head -->
# R(K6-e, K7-e) ≥ 70

[All records](../README.md) · witness [`K6e_K7e_n69.g6`](../graphs/K6e_K7e_n69.g6) (graph6) · [adjacency matrix](../graphs/K6e_K7e_n69.txt)

| Bound | Before | Upper bound | Status |
|---|---|---|---|
| R(K6-e, K7-e) ≥ **70** | 66 (1) | 124 [LidP] | current record |

1. R(K6-e, K7-e): before, 66 (S. P. Radziszowski, Small Ramsey Numbers, Electron. J. Combin. DS1.18 (24 April 2026), Table IIIa, lower bound [VO]).

The witness is a 69-vertex graph with no K6-e whose complement has no K7-e. Found 2026-11-20.
<!-- /generated:head -->

## How it was found

A *SAT step* is an exact search (CaDiCaL through PySAT) that deletes up to d vertices of the current graph and adds d + 1 new ones, keeping every other vertex and edge. Edges at the new vertices are the variables; every forbidden subgraph in a candidate is blocked by a new clause, and the search either returns a graph one vertex larger or proves that no graph of that form exists.

The start was a 68-vertex (K6-e, K7-e)-graph made of VO64 plus 4 vertices, a second witness of R(K6-e, K7-e) ≥ 69 found alongside [the published 68-vertex graph](K6e_K7e_n68.md). One step with d ≤ 3 found this 69-vertex graph after about 10.7 hours on a 64-core VM. It deleted VO64's vertices 21 and 47 and one of the added vertices, and added 4 new ones; the remaining 62 VO64 vertices keep their order and every edge among them.

On the 69-vertex graph the d ≤ 1 step is UNSAT. Earlier, adding 5 vertices directly to VO64 was split into 512 cubes: 505 were UNSAT and 7 never finished.

<!-- generated:tail -->
## The graph

- 69 vertices, 1061 edges, degrees 29–38; automorphism group of order 1 (nauty).
- Vertices 0–61 are the base graph [`VO_J5J7n64.g6`](../bases/VO_J5J7n64.g6) ([source](https://github.com/Steven-VO/circulant-Ramsey/blob/master/RamseyGraphs/Jn/J5J7n64.g6)) with its vertices 21, 47 deleted and the rest kept in order; every edge among them is unchanged. Vertices 62–68 are new; their neighbourhoods are in `records.json` (`extends.added_vertices`), and `verify.py` rebuilds the graph from the base and that list.

## Checks

| Claim | Checker | Result | Log |
|---|---|---|---|
| R(K6-e, K7-e) ≥ 70 | `checkers/check.c` | VALID | [K6e_K7e_n69.c.txt](../verification/K6e_K7e_n69.c.txt) |
| R(K6-e, K7-e) ≥ 70 | `checkers/check_networkx.py` | VALID | [K6e_K7e_n69.networkx.txt](../verification/K6e_K7e_n69.networkx.txt) |

```bash
cc -O2 -o check checkers/check.c
./check graphs/K6e_K7e_n69.g6 J6 J7
```

SHA-256 of `K6e_K7e_n69.g6`: `8771cb5034e318f639b5217b702cdb5696d1a818219749acaa926ac29e62deb6`
<!-- /generated:tail -->
