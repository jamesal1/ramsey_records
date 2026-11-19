/*
 * check.c: exact checker for two-colour Ramsey graphs avoiding K_s or K_s - e.
 *
 * A graph G on n vertices is a (A, B)-graph when G contains no A and the complement
 * of G contains no B. A and B are written K6 (complete graph K_6) or J6 (K_6 minus one
 * edge). Such a graph proves R(A, B) >= n + 1.
 *
 * Method (independent of checkers/check_networkx.py):
 *   K_s: depth-first clique search on bitsets.
 *   J_s: K_s - e consists of a clique S on s - 2 vertices plus two further vertices u, v
 *        that are both adjacent to all of S (u and v may or may not be adjacent). So H
 *        contains J_s iff some (s-2)-clique of H has at least two common neighbours.
 * Every witness is re-verified by counting the missing edges on its vertex set.
 *
 * Build and run:
 *   cc -O2 -o check checkers/check.c
 *   ./check graphs/K6e_K7e_n68.g6 J6 J7
 * The graph file holds one graph6 string, or n lines of n characters 0/1 (adjacency
 * matrix). Exit status: 0 valid, 1 invalid, 2 usage or input error.
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 1024
#define W ((MAXN + 63) / 64)

typedef struct { uint64_t w[W]; } set_t;

static int n, nw;
static set_t adj[MAXN];

static int popc(const set_t *a) {
    int c = 0;
    for (int i = 0; i < nw; i++) c += __builtin_popcountll(a->w[i]);
    return c;
}
static void and_(set_t *r, const set_t *a, const set_t *b) {
    for (int i = 0; i < nw; i++) r->w[i] = a->w[i] & b->w[i];
}
static int has(const set_t *a, int v) { return (a->w[v >> 6] >> (v & 63)) & 1; }
static void add(set_t *a, int v) { a->w[v >> 6] |= 1ULL << (v & 63); }
static void del(set_t *a, int v) { a->w[v >> 6] &= ~(1ULL << (v & 63)); }
static int first(const set_t *a) {
    for (int i = 0; i < nw; i++)
        if (a->w[i]) return i * 64 + __builtin_ctzll(a->w[i]);
    return -1;
}

static void die(const char *msg) {
    fprintf(stderr, "error: %s\n", msg);
    exit(2);
}

/* ---------------------------------------------------------------- input --- */

static char *read_file(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f) die("cannot open graph file");
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *buf = malloc(len + 1);
    if (!buf || fread(buf, 1, len, f) != (size_t)len) die("cannot read graph file");
    buf[len] = 0;
    fclose(f);
    return buf;
}

static void set_edge(int i, int j) {
    add(&adj[i], j);
    add(&adj[j], i);
}

static void parse_graph6(char *s) {
    if (!strncmp(s, ">>graph6<<", 10)) s += 10;
    size_t len = strcspn(s, "\r\n");
    s[len] = 0;
    for (size_t i = 0; i < len; i++)
        if (s[i] < 63 || s[i] > 126) die("bad graph6 character");
    unsigned char *p = (unsigned char *)s;
    if (p[0] == 126) {
        if (len >= 2 && p[1] == 126) die("graph too large");
        if (len < 4) die("truncated graph6");
        n = ((p[1] - 63) << 12) | ((p[2] - 63) << 6) | (p[3] - 63);
        p += 4;
        len -= 4;
    } else {
        n = p[0] - 63;
        p += 1;
        len -= 1;
    }
    if (n > MAXN) die("graph too large for MAXN");
    long need = (long)n * (n - 1) / 2;
    if ((long)len != (need + 5) / 6) die("graph6 length does not match vertex count");
    long k = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++, k++)
            if (((p[k / 6] - 63) >> (5 - k % 6)) & 1) set_edge(i, j);
}

static void parse_matrix(char *s) {
    char *rows[MAXN];
    int r = 0;
    for (char *line = strtok(s, "\r\n"); line; line = strtok(NULL, "\r\n")) {
        /* strip spaces and commas in place */
        char *o = line;
        for (char *c = line; *c; c++)
            if (*c != ' ' && *c != '\t' && *c != ',') *o++ = *c;
        *o = 0;
        if (!*line) continue;
        if (r >= MAXN) die("matrix too large");
        rows[r++] = line;
    }
    n = r;
    for (int i = 0; i < n; i++) {
        if ((int)strlen(rows[i]) != n) die("matrix is not square");
        if (rows[i][i] != '0') die("loop in matrix");
        for (int j = 0; j < n; j++) {
            if (rows[i][j] != '0' && rows[i][j] != '1') die("matrix entries must be 0/1");
            if (rows[i][j] != rows[j][i]) die("matrix is not symmetric");
            if (j > i && rows[i][j] == '1') set_edge(i, j);
        }
    }
}

/* --------------------------------------------------------------- search --- */

static int s_target, witness[MAXN];
static const set_t *g; /* adjacency of the graph being searched */

/* K_s: extend clique of size depth with candidates (higher-index common neighbours). */
static int find_K(int depth, set_t cand) {
    if (depth == s_target) return 1;
    if (popc(&cand) < s_target - depth) return 0;
    int v;
    while ((v = first(&cand)) >= 0) {
        del(&cand, v);
        if (popc(&cand) + 1 < s_target - depth) return 0;
        witness[depth] = v;
        set_t next;
        and_(&next, &cand, &g[v]);
        if (find_K(depth + 1, next)) return 1;
    }
    return 0;
}

/* J_s: enumerate (s-2)-cliques; `common` is the full common neighbourhood of the clique
 * so far, `cand` the part of it with index above the last chosen vertex. */
static int find_J(int depth, set_t common, set_t cand) {
    int core = s_target - 2;
    if (depth == core) {
        if (popc(&common) >= 2) {
            set_t c = common;
            int u = first(&c);
            del(&c, u);
            witness[core] = u;
            witness[core + 1] = first(&c);
            return 1;
        }
        return 0;
    }
    if (popc(&common) < core - depth + 2) return 0;
    int v;
    while ((v = first(&cand)) >= 0) {
        del(&cand, v);
        witness[depth] = v;
        set_t nc, nd;
        and_(&nc, &common, &g[v]);
        and_(&nd, &cand, &g[v]);
        if (find_J(depth + 1, nc, nd)) return 1;
    }
    return 0;
}

static int missing_edges(const set_t *a, int k) {
    int m = 0;
    for (int i = 0; i < k; i++)
        for (int j = i + 1; j < k; j++) {
            if (witness[i] == witness[j]) return 1 << 20; /* repeated vertex: invalid witness */
            m += !has(&a[witness[i]], witness[j]);
        }
    return m;
}

/* Returns 1 and fills witness[0..s-1] if `a` contains the forbidden graph. */
static int contains(const set_t *a, char kind, int s) {
    g = a;
    s_target = s;
    set_t all;
    memset(&all, 0, sizeof all);
    for (int v = 0; v < n; v++) add(&all, v);
    int found = (kind == 'K') ? find_K(0, all) : find_J(0, all, all);
    if (found) {
        int allowed = (kind == 'K') ? 0 : 1;
        if (missing_edges(a, s) > allowed) die("internal error: witness failed re-verification");
    }
    return found;
}

static void parse_forbidden(const char *spec, char *kind, int *s) {
    if ((spec[0] != 'K' && spec[0] != 'J' && spec[0] != 'k' && spec[0] != 'j') || !spec[1])
        die("forbidden graph must look like K6 or J7");
    *kind = (spec[0] == 'K' || spec[0] == 'k') ? 'K' : 'J';
    char *end;
    long v = strtol(spec + 1, &end, 10);
    if (*end || v < 3 || v > MAXN) die("forbidden graph must look like K6 or J7 (s >= 3)");
    *s = (int)v;
}

int main(int argc, char **argv) {
    if (argc != 4) {
        fprintf(stderr, "usage: %s GRAPH_FILE G_AVOIDS COMPLEMENT_AVOIDS   (e.g. J6 J7)\n", argv[0]);
        return 2;
    }
    char ka, kb;
    int sa, sb;
    parse_forbidden(argv[2], &ka, &sa);
    parse_forbidden(argv[3], &kb, &sb);

    char *buf = read_file(argv[1]);
    char *start = buf + strspn(buf, " \t\r\n");
    int is_matrix = (start[0] == '0' || start[0] == '1');
    if (is_matrix) parse_matrix(start);
    else parse_graph6(start);
    nw = (n + 63) / 64;

    static set_t comp[MAXN];
    long edges = 0;
    for (int i = 0; i < n; i++) {
        memset(&comp[i], 0, sizeof comp[i]);
        for (int j = 0; j < n; j++)
            if (j != i && !has(&adj[i], j)) add(&comp[i], j);
        edges += popc(&adj[i]);
    }
    edges /= 2;

    printf("checker: check.c (bitset clique search; J_s via (s-2)-clique with 2 common neighbours)\n");
    printf("file: %s\n", argv[1]);
    printf("vertices: %d\nedges: %ld\n", n, edges);

    int bad = 0;
    const char *where[2] = {"G", "complement"};
    char kinds[2] = {ka, kb};
    int sizes[2] = {sa, sb};
    for (int side = 0; side < 2; side++) {
        const set_t *a = side ? comp : adj;
        int f = contains(a, kinds[side], sizes[side]);
        printf("%s contains %c%d: %s", where[side], kinds[side], sizes[side], f ? "YES on" : "no");
        if (f) {
            for (int i = 0; i < sizes[side]; i++) printf(" %d", witness[i]);
            bad = 1;
        }
        printf("\n");
    }
    printf("result: %s\n", bad ? "INVALID" : "VALID");
    if (!bad) printf("proves: R(%c%d, %c%d) >= %d\n", ka, sa, kb, sb, n + 1);
    return bad;
}
