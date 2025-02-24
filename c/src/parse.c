#include <ctype.h>
#include <stdlib.h>
#include <string.h>

#include "gate.h"

static int ci_eq(const char *a, const char *b, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        if (tolower((unsigned char)a[i]) != tolower((unsigned char)b[i]))
            return 0;
    }
    return 1;
}

static const char *find_crlf(const char *p, const char *end)
{
    for (; p + 1 < end; p++) {
        if (p[0] == '\r' && p[1] == '\n')
            return p;
    }
    return NULL;
}

size_t gate_sizeof_request(void) { return sizeof(gate_request); }

int gate_parse_request(const char *buf, size_t len, gate_request *out)
{
    if (buf == NULL || out == NULL)
        return GATE_ERR_ARG;
    memset(out, 0, sizeof(*out));
    out->content_length = -1;
    const char *end = buf + len;
    const char *eol = find_crlf(buf, end);
    if (eol == NULL)
        return len > GATE_MAX_LINE ? GATE_ERR_TOO_LONG : 0;

    const char *sp1 = memchr(buf, ' ', (size_t)(eol - buf));
    if (sp1 == NULL)
        return GATE_ERR_SYNTAX;
    size_t mlen = (size_t)(sp1 - buf);
    if (mlen == 0 || mlen >= sizeof(out->method))
        return GATE_ERR_SYNTAX;
    for (size_t i = 0; i < mlen; i++) {
        if (!isupper((unsigned char)buf[i]))
            return GATE_ERR_SYNTAX;
    }
    memcpy(out->method, buf, mlen);

    const char *sp2 = memchr(sp1 + 1, ' ', (size_t)(eol - sp1 - 1));
    if (sp2 == NULL)
        return GATE_ERR_SYNTAX;
    size_t plen = (size_t)(sp2 - sp1 - 1);
    if (plen == 0 || plen >= sizeof(out->path) || sp1[1] != '/')
        return GATE_ERR_SYNTAX;
    memcpy(out->path, sp1 + 1, plen);

    if ((size_t)(eol - sp2 - 1) != 8 || !ci_eq(sp2 + 1, "HTTP/1.", 7))
        return GATE_ERR_SYNTAX;
    char minor = sp2[8];
    if (minor != '0' && minor != '1')
        return GATE_ERR_SYNTAX;
    out->version_minor = minor - '0';
    out->keep_alive = out->version_minor == 1;

    const char *line = eol + 2;
    for (;;) {
        const char *next = find_crlf(line, end);
        if (next == NULL)
            return (size_t)(end - line) > GATE_MAX_LINE ? GATE_ERR_TOO_LONG : 0;
        if (next == line)
            return (int)(next + 2 - buf);
        const char *colon = memchr(line, ':', (size_t)(next - line));
        if (colon == NULL || colon == line)
            return GATE_ERR_SYNTAX;
        if (++out->header_count > GATE_MAX_HEADERS)
            return GATE_ERR_TOO_MANY;
        size_t nlen = (size_t)(colon - line);
        const char *v = colon + 1;
        while (v < next && (*v == ' ' || *v == '\t'))
            v++;
        size_t vlen = (size_t)(next - v);
        if (nlen == 14 && ci_eq(line, "content-length", 14)) {
            char tmp[16];
            if (vlen == 0 || vlen >= sizeof(tmp))
                return GATE_ERR_SYNTAX;
            memcpy(tmp, v, vlen);
            tmp[vlen] = '\0';
            char *e = NULL;
            long n = strtol(tmp, &e, 10);
            if (*e != '\0' || n < 0 || n > 100000000L)
                return GATE_ERR_SYNTAX;
            out->content_length = (int32_t)n;
        } else if (nlen == 10 && ci_eq(line, "connection", 10)) {
            if (vlen == 5 && ci_eq(v, "close", 5))
                out->keep_alive = 0;
            else if (vlen == 10 && ci_eq(v, "keep-alive", 10))
                out->keep_alive = 1;
        }
        line = next + 2;
    }
}

int gate_header_get(const char *buf, size_t len, const char *name, char *out, size_t outlen)
{
    if (buf == NULL || name == NULL || out == NULL || outlen == 0)
        return GATE_ERR_ARG;
    const char *end = buf + len;
    size_t nlen = strlen(name);
    const char *line = find_crlf(buf, end);
    if (line == NULL)
        return 0;
    line += 2;
    for (;;) {
        const char *next = find_crlf(line, end);
        if (next == NULL || next == line)
            return 0;
        const char *colon = memchr(line, ':', (size_t)(next - line));
        if (colon != NULL && (size_t)(colon - line) == nlen && ci_eq(line, name, nlen)) {
            const char *v = colon + 1;
            while (v < next && (*v == ' ' || *v == '\t'))
                v++;
            size_t vlen = (size_t)(next - v);
            if (vlen >= outlen)
                return GATE_ERR_TOO_LONG;
            memcpy(out, v, vlen);
            out[vlen] = '\0';
            return (int)vlen;
        }
        line = next + 2;
    }
}
