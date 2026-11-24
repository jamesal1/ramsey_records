<!-- generated:head -->
# R(K5-e, K8-e) ≥ 67

[All records](../README.md) · witness [`K5e_K8e_n66.g6`](../graphs/K5e_K8e_n66.g6) (graph6) · [adjacency matrix](../graphs/K5e_K8e_n66.txt)

| Bound | Before | Upper bound | Status |
|---|---|---|---|
| R(K5-e, K8-e) ≥ **67** | 66 (1) | 91 [BZ3] | superseded by [≥ 68](K5e_K8e_n67.md) |

1. R(K5-e, K8-e): before, 66 (S. P. Radziszowski, Small Ramsey Numbers, Electron. J. Combin. DS1.18 (24 April 2026), Table IIIa, lower bound [Ea1]).

The witness is a 66-vertex graph with no K5-e whose complement has no K8-e. Found 2026-11-19.
<!-- /generated:head -->

## How it was found

An exact SAT search (CaDiCaL through PySAT, cube-and-conquer with lexicographic symmetry breaking) added 2 adjacent vertices to Van Overberghe's 64-vertex (K5-e, K7-e)-graph `J5J7n64` (VO64), the graph that proves R(K5-e, K7-e) = 65. Adding 3 vertices is UNSAT (46 s, cross-checked).

Superseded by [the 67-vertex graph](K5e_K8e_n67.md), one larger delete-and-add step from this one.

<!-- generated:tail -->
## The graph

- 66 vertices, 899 edges, degrees 18–28; automorphism group of order 120 (nauty).
- Vertices 0–63 are the base graph [`VO_J5J7n64.g6`](../bases/VO_J5J7n64.g6) ([source](https://github.com/Steven-VO/circulant-Ramsey/blob/master/RamseyGraphs/Jn/J5J7n64.g6)), same labelling; every edge among them is unchanged. Vertices 64–65 are new; their neighbourhoods are in `records.json` (`extends.added_vertices`), and `verify.py` rebuilds the graph from the base and that list.

## Checks

| Claim | Checker | Result | Log |
|---|---|---|---|
| R(K5-e, K8-e) ≥ 67 | `checkers/check.c` | VALID | [K5e_K8e_n66.c.txt](../verification/K5e_K8e_n66.c.txt) |
| R(K5-e, K8-e) ≥ 67 | `checkers/check_networkx.py` | VALID | [K5e_K8e_n66.networkx.txt](../verification/K5e_K8e_n66.networkx.txt) |
| R(K5-e, K8-e) ≥ 67 | `checkers/check_sage.py` | VALID | [K5e_K8e_n66.sage.txt](../verification/K5e_K8e_n66.sage.txt) |

```bash
cc -O2 -o check checkers/check.c
./check graphs/K5e_K8e_n66.g6 J5 J8
```

SHA-256 of `K5e_K8e_n66.g6`: `614b5df90e1525ea4b6aa7cf9888ccee07659f292f8aee79a4a3fdedbcee4518`
<!-- /generated:tail -->
