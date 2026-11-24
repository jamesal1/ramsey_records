<!-- generated:head -->
# R(K5-e, K8-e) ≥ 68

[All records](../README.md) · witness [`K5e_K8e_n67.g6`](../graphs/K5e_K8e_n67.g6) (graph6) · [adjacency matrix](../graphs/K5e_K8e_n67.txt)

| Bound | Before | Upper bound | Status |
|---|---|---|---|
| R(K5-e, K8-e) ≥ **68** | 66 (1) | 91 [BZ3] | current record |

1. R(K5-e, K8-e): before, 66 (S. P. Radziszowski, Small Ramsey Numbers, Electron. J. Combin. DS1.18 (24 April 2026), Table IIIa, lower bound [Ea1]).

The witness is a 67-vertex graph with no K5-e whose complement has no K8-e. Found 2026-11-20.
<!-- /generated:head -->

## How it was found

A *SAT step* is an exact search (CaDiCaL through PySAT) that deletes up to d vertices of the current graph and adds d + 1 new ones, keeping every other vertex and edge. Edges at the new vertices are the variables; every forbidden subgraph in a candidate is blocked by a new clause, and the search either returns a graph one vertex larger or proves that no graph of that form exists.

One step with d ≤ 3 from [the 66-vertex record](K5e_K8e_n66.md) (VO64 + 2 vertices). It deleted VO64's vertices 0 and 44 and one of the two added vertices, and added 4. The same step on the 67-vertex graph is UNSAT (40 min), so this line of search ends here.

<!-- generated:tail -->
## The graph

- 67 vertices, 911 edges, degrees 19–29; automorphism group of order 2 (nauty).
- Vertices 0–61 are the base graph [`VO_J5J7n64.g6`](../bases/VO_J5J7n64.g6) ([source](https://github.com/Steven-VO/circulant-Ramsey/blob/master/RamseyGraphs/Jn/J5J7n64.g6)) with its vertices 0, 44 deleted and the rest kept in order; every edge among them is unchanged. Vertices 62–66 are new; their neighbourhoods are in `records.json` (`extends.added_vertices`), and `verify.py` rebuilds the graph from the base and that list.

## Checks

| Claim | Checker | Result | Log |
|---|---|---|---|
| R(K5-e, K8-e) ≥ 68 | `checkers/check.c` | VALID | [K5e_K8e_n67.c.txt](../verification/K5e_K8e_n67.c.txt) |
| R(K5-e, K8-e) ≥ 68 | `checkers/check_networkx.py` | VALID | [K5e_K8e_n67.networkx.txt](../verification/K5e_K8e_n67.networkx.txt) |

```bash
cc -O2 -o check checkers/check.c
./check graphs/K5e_K8e_n67.g6 J5 J8
```

SHA-256 of `K5e_K8e_n67.g6`: `cc5f5d321a06225e6852aaf5ef6d213ba8ce0eeb6da0f5a4bcf734b21c8f97e7`
<!-- /generated:tail -->
