<!-- generated:head -->
# R(K5-e, K9-e) ≥ 72

[All records](../README.md) · witness [`K5e_K9e_n71.g6`](../graphs/K5e_K9e_n71.g6) (graph6) · [adjacency matrix](../graphs/K5e_K9e_n71.txt)

| Bound | Before | Upper bound | Status |
|---|---|---|---|
| R(K5-e, K9-e) ≥ **72** | 71 (1) | 136 [Ea1] | superseded by [≥ 77](K5e_K9e_n76.md) |

1. R(K5-e, K9-e): before, 71 (70-vertex disjoint union of Van Overberghe's 64-vertex (K5-e, K7-e)-graph and the octahedron: neither part contains K5-e, and the complement of the union is the join of the parts' complements, which has no K9-e. DS1.18 Table IIIa prints 69 [Ea1]).

The witness is a 71-vertex graph with no K5-e whose complement has no K9-e. Found 2026-11-19.
<!-- /generated:head -->

## How it was found

An exact SAT search (CaDiCaL through PySAT, cube-and-conquer with lexicographic symmetry breaking) added 7 vertices to Van Overberghe's 64-vertex (K5-e, K7-e)-graph `J5J7n64` (VO64), the graph that proves R(K5-e, K7-e) = 65; vertices 0–63 and their edges are unchanged.

DS1.18 prints 69 for this cell, but 71 already follows from the disjoint union of VO64 and the octahedron (see [the 76-vertex record](K5e_K9e_n76.md)), so this graph beat the known bound by one. It was superseded the same day by the 76-vertex graph, which climbs from that union.

<!-- generated:tail -->
## The graph

- 71 vertices, 958 edges, degrees 11–30; automorphism group of order 1 (nauty).
- Vertices 0–63 are the base graph [`VO_J5J7n64.g6`](../bases/VO_J5J7n64.g6) ([source](https://github.com/Steven-VO/circulant-Ramsey/blob/master/RamseyGraphs/Jn/J5J7n64.g6)), same labelling; every edge among them is unchanged. Vertices 64–70 are new; their neighbourhoods are in `records.json` (`extends.added_vertices`), and `verify.py` rebuilds the graph from the base and that list.

## Checks

| Claim | Checker | Result | Log |
|---|---|---|---|
| R(K5-e, K9-e) ≥ 72 | `checkers/check.c` | VALID | [K5e_K9e_n71.c.txt](../verification/K5e_K9e_n71.c.txt) |
| R(K5-e, K9-e) ≥ 72 | `checkers/check_networkx.py` | VALID | [K5e_K9e_n71.networkx.txt](../verification/K5e_K9e_n71.networkx.txt) |
| R(K5-e, K9-e) ≥ 72 | `checkers/check_sage.py` | VALID | [K5e_K9e_n71.sage.txt](../verification/K5e_K9e_n71.sage.txt) |

```bash
cc -O2 -o check checkers/check.c
./check graphs/K5e_K9e_n71.g6 J5 J9
```

SHA-256 of `K5e_K9e_n71.g6`: `5c38fe4b5f83bd9c8b7730eb5763a828b955fe3e830811959ff2e612dec7e1a9`
<!-- /generated:tail -->
