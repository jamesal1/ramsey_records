<!-- generated:head -->
# R(K5-e, K9-e) ≥ 77

[All records](../README.md) · witness [`K5e_K9e_n76.g6`](../graphs/K5e_K9e_n76.g6) (graph6) · [adjacency matrix](../graphs/K5e_K9e_n76.txt)

| Bound | Before | Upper bound | Status |
|---|---|---|---|
| R(K5-e, K9-e) ≥ **77** | 71 (1) | 136 [Ea1] | current record |

1. R(K5-e, K9-e): before, 71 (70-vertex disjoint union of Van Overberghe's 64-vertex (K5-e, K7-e)-graph and the octahedron: neither part contains K5-e, and the complement of the union is the join of the parts' complements, which has no K9-e. DS1.18 Table IIIa prints 69 [Ea1]).

The witness is a 76-vertex graph with no K5-e whose complement has no K9-e. Found 2026-11-19.
<!-- /generated:head -->

## How it was found

Seed: the disjoint union of Van Overberghe's 64-vertex (K5-e, K7-e)-graph `J5J7n64` (VO64), the graph that proves R(K5-e, K7-e) = 65 and the octahedron K2,2,2, a 70-vertex (K5-e, K9-e)-graph. The complement of a disjoint union is the join of the complements, so the largest clique (or clique minus an edge) in the complement of a union can be read off from the parts. The octahedron's complement is a perfect matching, which together with VO64's complement still has no K9-e. The seed alone proves R(K5-e, K9-e) ≥ 71.

A *SAT step* is an exact search (CaDiCaL through PySAT) that deletes up to d vertices of the current graph and adds d + 1 new ones, keeping every other vertex and edge. Edges at the new vertices are the variables; every forbidden subgraph in a candidate is blocked by a new clause, and the search either returns a graph one vertex larger or proves that no graph of that form exists.

Five steps with d ≤ 1 and one with d ≤ 2 climbed from 70 to 76 vertices; only added vertices were deleted, so vertices 0–63 are VO64 unchanged. On the 76-vertex graph, steps with d ≤ 1, d ≤ 2 (45 min) and d ≤ 3 (4.3 h) are all UNSAT.

<!-- generated:tail -->
## The graph

- 76 vertices, 1109 edges, degrees 10–31; automorphism group of order 2 (nauty).
- Vertices 0–63 are the base graph [`VO_J5J7n64.g6`](../bases/VO_J5J7n64.g6) ([source](https://github.com/Steven-VO/circulant-Ramsey/blob/master/RamseyGraphs/Jn/J5J7n64.g6)), same labelling; every edge among them is unchanged. Vertices 64–75 are new; their neighbourhoods are in `records.json` (`extends.added_vertices`), and `verify.py` rebuilds the graph from the base and that list.

## Checks

| Claim | Checker | Result | Log |
|---|---|---|---|
| R(K5-e, K9-e) ≥ 77 | `checkers/check.c` | VALID | [K5e_K9e_n76.c.txt](../verification/K5e_K9e_n76.c.txt) |
| R(K5-e, K9-e) ≥ 77 | `checkers/check_networkx.py` | VALID | [K5e_K9e_n76.networkx.txt](../verification/K5e_K9e_n76.networkx.txt) |

```bash
cc -O2 -o check checkers/check.c
./check graphs/K5e_K9e_n76.g6 J5 J9
```

SHA-256 of `K5e_K9e_n76.g6`: `125ac74702d6ce3f7bacb4ea3343f087e8dd4bf7aff00edf63b0f14bf5dfba29`
<!-- /generated:tail -->
