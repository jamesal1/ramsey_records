#!/usr/bin/env python3
"""
Exact checker for two-colour Ramsey graphs avoiding K_s or K_s - e, built on SageMath.

Method (independent of check.c and check_networkx.py):
  K_s: Graph.clique_number() (Cliquer) >= s, witness from Graph.clique_maximum().
  J_s: Graph.subgraph_search(K_s minus an edge, induced=False), Sage's generic
       non-induced subgraph search, i.e. the definition of containment.
Every witness is re-verified by counting edges on its vertex set.

Usage (with Sage's Python):  sage -python checkers/check_sage.py graphs/K6e_K7e_n68.g6 J6 J7
Exit status: 0 valid, 1 invalid, 2 usage or input error.
"""

import itertools
import os
import sys

from sage.all import Graph, graphs, version

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graph_io import load_graph, parse_forbidden  # noqa: E402


def find_forbidden(H, kind, s):
    if kind == "K":
        if H.clique_number() < s:
            return None
        return tuple(sorted(int(v) for v in H.clique_maximum()[:s]))
    F = graphs.CompleteGraph(s)
    F.delete_edge(0, 1)
    copy = H.subgraph_search(F, induced=False)
    return None if copy is None else tuple(sorted(int(v) for v in copy.vertices(sort=True)))


def missing_edges(H, verts):
    return sum(1 for u, v in itertools.combinations(verts, 2) if not H.has_edge(u, v))


def main():
    if len(sys.argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    path = sys.argv[1]
    try:
        forb = [parse_forbidden(sys.argv[2]), parse_forbidden(sys.argv[3])]
        n, edges = load_graph(path)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    G = Graph(n)
    G.add_edges(edges)
    print(f"checker: check_sage.py ({version()}; Cliquer clique number, non-induced subgraph_search)")
    print(f"file: {path}")
    print(f"vertices: {n}\nedges: {len(edges)}")
    bad = False
    for H, (kind, s), where in ((G, forb[0], "G"), (G.complement(), forb[1], "complement")):
        w = find_forbidden(H, kind, s)
        if w is None:
            print(f"{where} contains {kind}{s}: no")
        else:
            assert len(w) == s and missing_edges(H, w) <= (0 if kind == "K" else 1)
            print(f"{where} contains {kind}{s}: YES on {' '.join(map(str, w))}")
            bad = True
    print(f"result: {'INVALID' if bad else 'VALID'}")
    if not bad:
        (ka, sa), (kb, sb) = forb
        print(f"proves: R({ka}{sa}, {kb}{sb}) >= {n + 1}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
