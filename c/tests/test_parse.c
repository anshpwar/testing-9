#include <stdio.h>
#include <string.h>

#include "check.h"
#include "gate.h"

#define REQ(s) s, strlen(s)

static void test_valid_request(void)
{
    gate_request r;
    const char *text = "GET /v1/users?id=7 HTTP/1.1\r\nHost: api.example.invalid\r\nContent-Length: 12\r\nConnection: close\r\n\r\nbody";
    int n = gate_parse_request(REQ(text), &r);
    CHECK(n > 0);
    CHECK((size_t)n == strlen(text) - 4);
    CHECK(strcmp(r.method, "GET") == 0);
    CHECK(strcmp(r.path, "/v1/users?id=7") == 0);
    CHECK_EQ(r.version_minor, 1);
    CHECK_EQ(r.header_count, 3);
    CHECK_EQ(r.content_length, 12);
    CHECK_EQ(r.keep_alive, 0);
}

static void test_defaults(void)
{
    gate_request r;
    CHECK(gate_parse_request(REQ("POST / HTTP/1.0\r\n\r\n"), &r) > 0);
    CHECK_EQ(r.content_length, -1);
    CHECK_EQ(r.keep_alive, 0);
    CHECK(gate_parse_request(REQ("POST / HTTP/1.1\r\n\r\n"), &r) > 0);
    CHECK_EQ(r.keep_alive, 1);
}

static void test_incomplete_heads(void)
{
    gate_request r;
    CHECK_EQ(gate_parse_request(REQ("GET / HTTP/1.1"), &r), 0);
    CHECK_EQ(gate_parse_request(REQ("GET / HTTP/1.1\r\nHost: x\r\n"), &r), 0);
}

static void test_syntax_errors(void)
{
    gate_request r;
    CHECK_EQ(gate_parse_request(REQ("get / HTTP/1.1\r\n\r\n"), &r), GATE_ERR_SYNTAX);
    CHECK_EQ(gate_parse_request(REQ("GET noslash HTTP/1.1\r\n\r\n"), &r), GATE_ERR_SYNTAX);
    CHECK_EQ(gate_parse_request(REQ("GET / HTTP/2.0\r\n\r\n"), &r), GATE_ERR_SYNTAX);
    CHECK_EQ(gate_parse_request(REQ("GET / HTTP/1.1\r\nNoColon\r\n\r\n"), &r), GATE_ERR_SYNTAX);
    CHECK_EQ(gate_parse_request(REQ("GET / HTTP/1.1\r\nContent-Length: abc\r\n\r\n"), &r), GATE_ERR_SYNTAX);
    CHECK_EQ(gate_parse_request(REQ("GET / HTTP/1.1\r\nContent-Length: -5\r\n\r\n"), &r), GATE_ERR_SYNTAX);
    CHECK_EQ(gate_parse_request(NULL, 0, &r), GATE_ERR_ARG);
}

static void test_header_limits(void)
{
    gate_request r;
    char big[8192];
    size_t used = (size_t)snprintf(big, sizeof(big), "GET / HTTP/1.1\r\n");
    for (int i = 0; i < GATE_MAX_HEADERS + 1; i++)
        used += (size_t)snprintf(big + used, sizeof(big) - used, "X-%d: v\r\n", i);
    used += (size_t)snprintf(big + used, sizeof(big) - used, "\r\n");
    CHECK_EQ(gate_parse_request(big, used, &r), GATE_ERR_TOO_MANY);
}

static void test_header_get(void)
{
    const char *text = "GET / HTTP/1.1\r\nX-Api-Key:   abc123\r\nHost: h\r\n\r\n";
    char out[32];
    CHECK_EQ(gate_header_get(REQ(text), "x-api-key", out, sizeof(out)), 6);
    CHECK(strcmp(out, "abc123") == 0);
    CHECK_EQ(gate_header_get(REQ(text), "missing", out, sizeof(out)), 0);
    CHECK_EQ(gate_header_get(REQ(text), "x-api-key", out, 3), GATE_ERR_TOO_LONG);
}

static void test_layout(void)
{
    CHECK_EQ(gate_sizeof_request(), sizeof(gate_request));
    CHECK_EQ(sizeof(gate_request), 152);
}

int main(void)
{
    test_valid_request();
    test_defaults();
    test_incomplete_heads();
    test_syntax_errors();
    test_header_limits();
    test_header_get();
    test_layout();
    CHECK_DONE();
}
