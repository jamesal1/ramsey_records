"""
Graph file input and output shared by the Python checkers and tools. Standard library only.

Graph files hold either one graph6 string or n lines of n characters 0/1 (adjacency matrix).
Forbidden graphs are written "K6" (complete graph K_6) or "J6" (K_6 minus one edge).
"""

import hashlib
import re


def parse_forbidden(spec):
    """'K6' -> ('K', 6); 'J7' -> ('J', 7)."""
    m = re.fullmatch(r"([KJ])(\d+)", spec.strip().upper())
    if not m or int(m.group(2)) < 3:
        raise ValueError(f"forbidden graph must look like K6 or J7, got {spec!r}")
    return m.group(1), int(m.group(2))


def survey_name(spec):
    """'J6' -> 'K6-e', 'K8' -> 'K8' (the notation of Radziszowski's survey)."""
    kind, s = parse_forbidden(spec)
    return f"K{s}-e" if kind == "J" else f"K{s}"


def decode_graph6(s):
    """Decode one graph6 string into (n, sorted list of edges (i, j) with i < j)."""
    s = s.strip()
    if s.startswith(">>graph6<<"):
        s = s[10:]
    data = [ord(c) - 63 for c in s]
    if not data or any(x < 0 or x > 63 for x in data):
        raise ValueError("not a graph6 string")
    if data[0] == 63:
        if len(data) > 1 and data[1] == 63:
            raise ValueError("graphs this large are not supported")
        n = (data[1] << 12) | (data[2] << 6) | data[3]
        body = data[4:]
    else:
        n = data[0]
        body = data[1:]
    need = n * (n - 1) // 2
    if len(body) != (need + 5) // 6:
        raise ValueError(f"graph6 body has {len(body)} bytes, expected {(need + 5) // 6} for n={n}")
    edges = []
    k = 0
    for j in range(1, n):
        for i in range(j):
            if (body[k // 6] >> (5 - k % 6)) & 1:
                edges.append((i, j))
            k += 1
    return n, sorted(edges)


def encode_graph6(n, edges):
    if n > 258047:
        raise ValueError("graph too large")
    eset = {(min(e), max(e)) for e in edges}
    bits = [1 if (i, j) in eset else 0 for j in range(1, n) for i in range(j)]
    bits += [0] * (-len(bits) % 6)
    head = chr(n + 63) if n < 63 else "~" + "".join(chr(((n >> sh) & 63) + 63) for sh in (12, 6, 0))
    body = "".join(chr(63 + int("".join(map(str, bits[k:k + 6])), 2)) for k in range(0, len(bits), 6))
    return head + body


def decode_matrix(text):
    rows = [re.sub(r"[\s,]", "", ln) for ln in text.splitlines() if ln.strip()]
    n = len(rows)
    if any(len(r) != n or set(r) - {"0", "1"} for r in rows):
        raise ValueError("adjacency matrix must be n rows of n 0/1 entries")
    for i in range(n):
        if rows[i][i] != "0":
            raise ValueError(f"loop at vertex {i}")
        for j in range(i):
            if rows[i][j] != rows[j][i]:
                raise ValueError(f"matrix not symmetric at ({j}, {i})")
    return n, sorted((i, j) for j in range(n) for i in range(j) if rows[i][j] == "1")


def matrix_text(n, edges):
    A = [["0"] * n for _ in range(n)]
    for i, j in edges:
        A[i][j] = A[j][i] = "1"
    return "".join("".join(r) + "\n" for r in A)


def load_graph(path):
    """Return (n, sorted edge list) from a graph6 or 0/1-matrix file."""
    with open(path) as f:
        text = f.read()
    first = text.strip()[:1]
    if first in ("0", "1"):
        return decode_matrix(text)
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) != 1:
        raise ValueError(f"{path}: expected exactly one graph6 string, found {len(lines)} lines")
    return decode_graph6(lines[0])


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()
