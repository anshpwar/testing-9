#ifndef GATE_H
#define GATE_H

#include <stddef.h>
#include <stdint.h>

#define GATE_MAX_LINE 4096
#define GATE_MAX_HEADERS 64

enum {
    GATE_OK = 0,
    GATE_ERR_ARG = -1,
    GATE_ERR_SYNTAX = -2,
    GATE_ERR_TOO_LONG = -3,
    GATE_ERR_TOO_MANY = -4
};

/* Parsed request line plus the headers the gateway acts on. Mirrored by gatekit/native.py. */
typedef struct {
    char method[8];
    char path[128];
    int32_t version_minor;
    int32_t header_count;
    int32_t content_length; /* -1 when absent */
    int32_t keep_alive;
} gate_request;

/* Token bucket in millitokens so fractional refills accumulate without floating point. */
typedef struct {
    int64_t capacity_milli;
    int64_t tokens_milli;
    int64_t refill_per_s_milli;
    int64_t last_ts_ms;
} gate_bucket;

/* Returns bytes consumed through the blank line, 0 when the head is incomplete, or a negative error. */
int gate_parse_request(const char *buf, size_t len, gate_request *out);

/* Case-insensitive header lookup in a request head; returns value length, 0 when absent, negative on error. */
int gate_header_get(const char *buf, size_t len, const char *name, char *out, size_t outlen);

int gate_bucket_init(gate_bucket *b, int64_t capacity, int64_t refill_per_s, int64_t now_ms);
/* 1 = allowed, 0 = denied, negative = error. */
int gate_bucket_take(gate_bucket *b, int64_t cost, int64_t now_ms);
/* Milliseconds until `cost` tokens are available, or -1 if the bucket never refills. */
int64_t gate_bucket_retry_after_ms(const gate_bucket *b, int64_t cost);

size_t gate_sizeof_request(void);
size_t gate_sizeof_bucket(void);

#endif
