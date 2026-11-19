#!/usr/bin/env python3
"""
Exact checker for two-colour Ramsey graphs avoiding K_s or K_s - e, built on NetworkX.

A graph G on n vertices is a (A, B)-graph when G contains no A and the complement of G
contains no B. Such a graph proves R(A, B) >= n + 1.

Method (independent of check.c and check_sage.py):
  K_s: enumerate cliques with nx.enumerate_all_cliques; G has K_s iff one has size s.
  J_s: K_s - e is exactly two K_{s-1} sharing s-2 vertices (the endpoints of the missing
       edge are the two vertices outside the shared part). So H has J_s iff H has K_s,
       or some (s-2)-set lies in two different (s-1)-cliques.
Every witness is re-verified by counting edges on its vertex set.

Usage:  python checkers/check_networkx.py graphs/K6e_K7e_n68.g6 J6 J7
Exit status: 0 valid, 1 invalid, 2 usage or input error.
"""

import itertools
import os
import sys

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graph_io import load_graph, parse_forbidden  # noqa: E402


def find_forbidden(H, kind, s):
    """Return a vertex tuple spanning K_s (kind 'K') or K_s - e (kind 'J') in H, else None."""
    seen = {}
    for clique in nx.enumerate_all_cliques(H):  # non-decreasing size
        size = len(clique)
        if size == s:
            return tuple(sorted(clique))
        if kind == "J" and size == s - 1:
            cset = frozenset(clique)
            for core in itertools.combinations(sorted(clique), s - 2):
                other = seen.setdefault(core, cset)
                if other != cset:
                    return tuple(sorted(other | cset))
        if size > s:
            break
    return None


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
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
    print(f"checker: check_networkx.py (networkx {nx.__version__}; J_s via two (s-1)-cliques sharing s-2 vertices)")
    print(f"file: {path}")
    print(f"vertices: {n}\nedges: {len(edges)}")
    bad = False
    for H, (kind, s), where in ((G, forb[0], "G"), (nx.complement(G), forb[1], "complement")):
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
