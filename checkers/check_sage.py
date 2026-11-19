#!/usr/bin/env python3
"""
Exact checker for two-colour Ramsey graphs avoiding K_s or K_s - e, built on SageMath.

Method (independent of check.c and check_networkx.py):
  K_s: Graph.clique_number() (Cliquer) >= s, witness from Graph.clique_maximum().
  J_s: Graph.subgraph_search(K_s minus an edge, induced=False), Sage's generic
       non-induced subgraph search, i.e. the definition of containment.
Every witness is re-verified by counting edges on its vertex set.

The graph file is read by Sage's own graph6 and adjacency-matrix readers, so this checker
shares no code with the other two, not even file parsing.

Usage (with Sage's Python):  sage -python checkers/check_sage.py graphs/K6e_K7e_n68.g6 J6 J7
Exit status: 0 valid, 1 invalid, 2 usage or input error.
"""

import itertools
import re
import sys

from sage.all import ZZ, Graph, graphs, matrix
from sage.version import version


def parse_forbidden(spec):
    m = re.fullmatch(r"([KJ])(\d+)", spec.strip().upper())
    if not m or int(m.group(2)) < 3:
        raise ValueError(f"forbidden graph must look like K6 or J7, got {spec!r}")
    return m.group(1), int(m.group(2))


def load_graph(path):
    """Read a graph6 string or a 0/1 adjacency matrix with Sage's own readers."""
    with open(path) as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    if not lines:
        raise ValueError("empty graph file")
    if lines[0][0] in "01":
        rows = [[int(c) for c in re.sub(r"[\s,]", "", ln)] for ln in lines]
        return Graph(matrix(ZZ, rows), format="adjacency_matrix")
    if len(lines) != 1:
        raise ValueError(f"expected exactly one graph6 string, found {len(lines)} lines")
    return Graph(lines[0], format="graph6")


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
        G = load_graph(path)
    except (OSError, ValueError, TypeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if G.has_loops() or G.has_multiple_edges():
        print("error: graph has loops or multiple edges", file=sys.stderr)
        return 2
    n = G.order()
    print(f"checker: check_sage.py (SageMath {version}; Sage graph6/matrix readers, "
          f"Cliquer clique number, non-induced subgraph_search)")
    print(f"file: {path}")
    print(f"vertices: {n}\nedges: {G.size()}")
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
