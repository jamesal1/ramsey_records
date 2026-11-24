# New lower bounds for small Ramsey numbers

Explicit graphs that improve lower bounds for two-colour Ramsey numbers R(A, B), where A and B are
complete graphs K_k or complete graphs minus one edge, K_k − e. They are compared with
Radziszowski's dynamic survey *Small Ramsey Numbers* (Electron. J. Combin. DS1.18, 24 April 2026),
Tables I and IIIa, and with later results we know of.

A graph G on n vertices with no A in G and no B in its complement proves R(A, B) ≥ n + 1.

Each record has its own page, linked from the "How it was found" column, with the search that found
the graph, what was tried around it, the graph's structure and its checks. "Before" is the best lower
bound known without these graphs: the survey's value, or one derived from published results where the
survey prints none or a derivation gives more (each page gives the source). One graph can prove
several cells; it then appears once per cell.

<!-- records-table:start -->
| Bound | Before | Upper bound | Witness | How it was found | Found |
|---|---|---|---|---|---|
| **R(K4-e, K11) ≥ 56** | 52 | – | [`K4e_K11_n55.g6`](graphs/K4e_K11_n55.g6) | [Cayley graph on SmallGroup(55,1)](records/K4e_K11_n55.md) | 2026-11-22 |
| **R(K4-e, K12-e) ≥ 56** | 52 | – | [`K4e_K11_n55.g6`](graphs/K4e_K11_n55.g6) | [Cayley graph on SmallGroup(55,1)](records/K4e_K11_n55.md) | 2026-11-22 |
| **R(K4-e, K12) ≥ 60** | 58 | – | [`K4e_K12_n59.g6`](graphs/K4e_K12_n59.g6) | [VO48 ⊔ 6-vertex graph, then a SAT ladder](records/K4e_K12_n59.md) | 2026-11-20 |
| **R(K4-e, K13) ≥ 65** | 61 | – | [`K4e_K13_n64.g6`](graphs/K4e_K13_n64.g6) | [Cayley graph on SmallGroup(64,4)](records/K4e_K13_n64.md) | 2026-11-22 |
| **R(K4-e, K14-e) ≥ 65** | 61 | – | [`K4e_K13_n64.g6`](graphs/K4e_K13_n64.g6) | [Cayley graph on SmallGroup(64,4)](records/K4e_K13_n64.md) | 2026-11-22 |
| **R(K4-e, K14) ≥ 76** | 67 | – | [`K4e_K14_n75.g6`](graphs/K4e_K14_n75.g6) | [Cayley graph on SmallGroup(75,2)](records/K4e_K14_n75.md) | 2026-11-22 |
| **R(K4-e, K15-e) ≥ 76** | 69 | – | [`K4e_K14_n75.g6`](graphs/K4e_K14_n75.g6) | [Cayley graph on SmallGroup(75,2)](records/K4e_K14_n75.md) | 2026-11-22 |
| **R(K4-e, K15) ≥ 81** | 74 | – | [`K4e_K15_n80.g6`](graphs/K4e_K15_n80.g6) | [Cayley graph on SmallGroup(80,3)](records/K4e_K15_n80.md) | 2026-11-22 |
| **R(K5-e, K8-e) ≥ 68** | 66 | 91 [BZ3] | [`K5e_K8e_n67.g6`](graphs/K5e_K8e_n67.g6) | [SAT ladder from the 66-vertex record](records/K5e_K8e_n67.md) | 2026-11-20 |
| **R(K5-e, K8) ≥ 73** | 69 | 117 [BZ3] | [`K5e_K8_n72.g6`](graphs/K5e_K8_n72.g6) | [SAT ladder from the 71-vertex record](records/K5e_K8_n72.md) | 2026-11-20 |
| **R(K5-e, K9-e) ≥ 77** | 71 | 136 [Ea1] | [`K5e_K9e_n76.g6`](graphs/K5e_K9e_n76.g6) | [VO64 ⊔ octahedron, then a SAT ladder](records/K5e_K9e_n76.md) | 2026-11-19 |
| **R(K5-e, K9) ≥ 81** | 75 | 169 [BZ3] | [`K5e_K9_n80.g6`](graphs/K5e_K9_n80.g6) | [Cayley graph on Z4 × Z4 × Z5](records/K5e_K9_n80.md) | 2026-11-20 |
| **R(K5-e, K10-e) ≥ 97** | 77 | 188 [BZ3] | [`K5e_K10e_n96.g6`](graphs/K5e_K10e_n96.g6) | [Cayley graph on SmallGroup(96,12)](records/K5e_K10e_n96.md) | 2026-11-21 |
| **R(K5-e, K10) ≥ 97** | 92 | 233 [BZ3] | [`K5e_K10e_n96.g6`](graphs/K5e_K10e_n96.g6) | [Cayley graph on SmallGroup(96,12)](records/K5e_K10e_n96.md) | 2026-11-21 |
| **R(K5-e, K11-e) ≥ 101** | 92 | 261 [BZ3] | [`K5e_K11e_n100.g6`](graphs/K5e_K11e_n100.g6) | [SmallGroup(96,12) Cayley graph + 4 vertices by SAT](records/K5e_K11e_n100.md) | 2026-11-23 |
| **R(K5, K12) ≥ 225** | 203 | 672 [AnM3/AnM4] | [`K5_K12_n224.g6`](graphs/K5_K12_n224.g6) | [Cayley graph on Z16 × Z2 × Z7 (multiplier orbits)](records/K5_K12_n224.md) | 2026-11-24 |
| **R(K6-e, K7-e) ≥ 70** | 66 | 124 [LidP] | [`K6e_K7e_n69.g6`](graphs/K6e_K7e_n69.g6) | [SAT ladder from a 68-vertex VO64 + 4 graph](records/K6e_K7e_n69.md) | 2026-11-20 |
| **R(K6, K8-e) ≥ 117** | 115 | 353 [BZ4] | [`K6_K8e_n116.g6`](graphs/K6_K8e_n116.g6) | [Circulant on Z116](records/K6_K8e_n116.md) | 2026-11-21 |
| **R(K6, K9-e) ≥ 146** | 135 | 615 [BZ3] | [`K6_K9e_n145.g6`](graphs/K6_K9e_n145.g6) | [Circulant on Z145 (multiplier orbits)](records/K6_K9e_n145.md) | 2026-11-24 |
| **R(K7-e, K8-e) ≥ 117** | 115 | 432 [BZ3] | [`K6_K8e_n116.g6`](graphs/K6_K8e_n116.g6) | [Circulant on Z116](records/K6_K8e_n116.md) | 2026-11-21 |
| **R(K7-e, K9-e) ≥ 146** | 135 | 761 [BZ3] | [`K6_K9e_n145.g6`](graphs/K6_K9e_n145.g6) | [Circulant on Z145 (multiplier orbits)](records/K6_K9e_n145.md) | 2026-11-24 |

Earlier records, since superseded. Each page says how the graph was found and what replaced it.

| Bound | Before | Witness | How it was found | Found | Superseded by |
|---|---|---|---|---|---|
| R(K5-e, K8-e) ≥ 67 | 66 | [`K5e_K8e_n66.g6`](graphs/K5e_K8e_n66.g6) | [VO64 + 2 vertices by SAT](records/K5e_K8e_n66.md) | 2026-11-19 | [≥ 68](records/K5e_K8e_n67.md) |
| R(K5-e, K8) ≥ 72 | 69 | [`K5e_K8_n71.g6`](graphs/K5e_K8_n71.g6) | [VO64 ⊔ K4, then a SAT ladder](records/K5e_K8_n71.md) | 2026-11-20 | [≥ 73](records/K5e_K8_n72.md) |
| R(K5-e, K8) ≥ 71 | 69 | [`K5e_K8_n70.g6`](graphs/K5e_K8_n70.g6) | [VO64 + 6 vertices by SAT](records/K5e_K8_n70.md) | 2026-11-19 | [≥ 72](records/K5e_K8_n71.md) |
| R(K5-e, K9-e) ≥ 72 | 71 | [`K5e_K9e_n71.g6`](graphs/K5e_K9e_n71.g6) | [VO64 + 7 vertices by SAT](records/K5e_K9e_n71.md) | 2026-11-19 | [≥ 77](records/K5e_K9e_n76.md) |
| R(K5-e, K9) ≥ 80 | 75 | [`K5e_K9_n79.g6`](graphs/K5e_K9_n79.g6) | [VO64 ⊔ 10-vertex graph, then a SAT ladder](records/K5e_K9_n79.md) | 2026-11-20 | [≥ 81](records/K5e_K9_n80.md) |
| R(K5-e, K10-e) ≥ 81 | 77 | [`K5e_K9_n80.g6`](graphs/K5e_K9_n80.g6) | [Cayley graph on Z4 × Z4 × Z5](records/K5e_K9_n80.md) | 2026-11-20 | [≥ 97](records/K5e_K10e_n96.md) |
| R(K5-e, K10-e) ≥ 80 | 77 | [`K5e_K9_n79.g6`](graphs/K5e_K9_n79.g6) | [VO64 ⊔ 10-vertex graph, then a SAT ladder](records/K5e_K9_n79.md) | 2026-11-20 | [≥ 81](records/K5e_K9_n80.md) |
| R(K5-e, K11-e) ≥ 97 | 92 | [`K5e_K11e_n96.g6`](graphs/K5e_K11e_n96.g6) | [Cayley graph on Z4 × Z4 × Z2 × Z3](records/K5e_K11e_n96.md) | 2026-11-20 | [≥ 101](records/K5e_K11e_n100.md) |
| R(K6-e, K7-e) ≥ 69 | 66 | [`K6e_K7e_n68.g6`](graphs/K6e_K7e_n68.g6) | [VO64 + 4 vertices by SAT](records/K6e_K7e_n68.md) | 2026-11-18 | [≥ 70](records/K6e_K7e_n69.md) |
<!-- records-table:end -->

## How they were found

Three kinds of search produced these graphs; the page for each record gives the details.

- **Extending a published graph by SAT.** Start from a published record graph, usually
  Steven Van Overberghe's 64-vertex graph that proves R(K5 − e, K7 − e) = 65
  ([circulant-Ramsey](https://github.com/Steven-VO/circulant-Ramsey), `RamseyGraphs/Jn/`), or its
  disjoint union with a small graph, and add vertices with an exact SAT search, possibly deleting a
  few vertices first. Such records state their base graph and their exact difference from it
  (`extends` in `records.json`), and `verify.py` rebuilds them from that.
- **Cayley graphs.** Choose a group and search by SAT for a connection set. For abelian groups the
  connection set is in `records.json` (`structure`) and on the page, and `verify.py` rebuilds the
  graph from it.
- **A Cayley graph extended by SAT**, combining the two.

Claude (Anthropic's AI assistant) was used to generate the code for these searches: the SAT
encodings, the extension and Cayley searches and the OpenEvolve set-up. It also generated the
checkers and tools in this repository. The results do not depend on trusting the search code. Each
graph is an explicit witness, and anyone can check it with the independent checkers below or with
their own.

## Check them yourself

```bash
cc -O2 -o check checkers/check.c
./check graphs/K6e_K7e_n68.g6 J6 J7
```

Arguments are the graph file, what G must avoid and what its complement must avoid
(`J6` = K6 − e, `K8` = K8). Each check takes at most a few seconds; each record's page lists the
commands for every cell it claims.

To verify every record (hashes, files, diffs from base graphs, Cayley connection sets, and the C
checker on every claimed cell):

```bash
python verify.py
python verify.py --checkers c,networkx,sage   # also NetworkX and Sage (slow on the largest graphs)
```

Three independent checkers are provided. Each one uses a different test for K_s − e:

| Checker | K_s | K_s − e |
|---|---|---|
| `checkers/check.c` | bitset clique search | an (s−2)-clique with two common neighbours |
| `checkers/check_networkx.py` | NetworkX clique enumeration | two (s−1)-cliques sharing s−2 vertices |
| `checkers/check_sage.py` | Sage `clique_number` (Cliquer) | Sage `subgraph_search(..., induced=False)` |

Every witness a checker reports is re-verified by counting edges. The outputs from when each
record was added are in `verification/`. NetworkX enumerates every clique and is impractical on the
largest graphs (for example the 224-vertex R(K5, K12) witness, whose complement is 140-regular).
Records added since 2026-11-24 were checked independently when they were found (C plus NetworkX or
Sage) and again here with the C checker; their pages and `prior_verification` in `records.json` say so.

## Files

- `graphs/`: each witness as a graph6 string (`.g6`) and as an n × n 0/1 adjacency matrix (`.txt`).
- `records/`: one page per witness: how it was found, its structure and its checks.
- `bases/`: the published graphs the witnesses extend; `bases/sources.json` gives their sources and hashes.
- `records.json`: one entry per witness: the cell (and `also_proves` for other cells), bounds before
  and after with sources, SHA-256 of both files, the exact difference from the base graph or the
  Cayley connection set, nauty invariants, and the checker results.
- `verification/`: checker output for each record.
- `checkers/`: the three checkers.
- `verify.py`: re-checks everything.
- `tools/publish.py`, `PUBLISHING.md`: how records are added and released.

## How to cite

See `CITATION.cff`. A Zenodo DOI is minted for each GitHub release.

## Licence

Apache License 2.0 (see `LICENSE`).
