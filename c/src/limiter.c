#include "gate.h"

#define MAX_ELAPSED_MS 86400000LL

size_t gate_sizeof_bucket(void) { return sizeof(gate_bucket); }

int gate_bucket_init(gate_bucket *b, int64_t capacity, int64_t refill_per_s, int64_t now_ms)
{
    if (b == NULL || capacity <= 0 || refill_per_s < 0 || capacity > 1000000000LL)
        return GATE_ERR_ARG;
    b->capacity_milli = capacity * 1000;
    b->tokens_milli = capacity * 1000;
    b->refill_per_s_milli = refill_per_s * 1000;
    b->last_ts_ms = now_ms;
    return GATE_OK;
}

int gate_bucket_take(gate_bucket *b, int64_t cost, int64_t now_ms)
{
    if (b == NULL || cost <= 0)
        return GATE_ERR_ARG;
    if (now_ms < b->last_ts_ms)
        now_ms = b->last_ts_ms; /* a clock that went backwards earns nothing */
    int64_t elapsed = now_ms - b->last_ts_ms;
    if (elapsed > MAX_ELAPSED_MS)
        elapsed = MAX_ELAPSED_MS;
    int64_t add = elapsed * b->refill_per_s_milli / 1000;
    if (add > 0) {
        b->tokens_milli += add;
        if (b->tokens_milli > b->capacity_milli)
            b->tokens_milli = b->capacity_milli;
        b->last_ts_ms = now_ms; /* only advance when something was earned, so fractions accumulate */
    }
    int64_t need = cost * 1000;
    if (b->tokens_milli >= need) {
        b->tokens_milli -= need;
        return 1;
    }
    return 0;
}

int64_t gate_bucket_retry_after_ms(const gate_bucket *b, int64_t cost)
{
    if (b == NULL || cost <= 0)
        return GATE_ERR_ARG;
    int64_t deficit = cost * 1000 - b->tokens_milli;
    if (deficit <= 0)
        return 0;
    if (b->refill_per_s_milli == 0)
        return -1;
    return (deficit * 1000 + b->refill_per_s_milli - 1) / b->refill_per_s_milli;
}
