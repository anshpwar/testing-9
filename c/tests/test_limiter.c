#include "check.h"
#include "gate.h"

static void test_burst_then_deny(void)
{
    gate_bucket b;
    CHECK_EQ(gate_bucket_init(&b, 3, 1, 0), GATE_OK);
    CHECK_EQ(gate_bucket_take(&b, 1, 0), 1);
    CHECK_EQ(gate_bucket_take(&b, 1, 0), 1);
    CHECK_EQ(gate_bucket_take(&b, 1, 0), 1);
    CHECK_EQ(gate_bucket_take(&b, 1, 0), 0);
}

static void test_refill_over_time(void)
{
    gate_bucket b;
    gate_bucket_init(&b, 2, 2, 0);
    gate_bucket_take(&b, 2, 0);
    CHECK_EQ(gate_bucket_take(&b, 1, 100), 0);  /* 0.2 tokens */
    CHECK_EQ(gate_bucket_take(&b, 1, 500), 1);  /* 1.0 token */
    CHECK_EQ(gate_bucket_take(&b, 1, 500), 0);
}

static void test_fractions_accumulate(void)
{
    gate_bucket b;
    gate_bucket_init(&b, 1, 1, 0);
    gate_bucket_take(&b, 1, 0);
    int allowed = 0;
    for (int t = 1; t <= 1000; t++)
        allowed += gate_bucket_take(&b, 1, t);
    CHECK_EQ(allowed, 1);
}

static void test_capacity_caps_refill(void)
{
    gate_bucket b;
    gate_bucket_init(&b, 2, 100, 0);
    gate_bucket_take(&b, 1, 0);
    CHECK_EQ(gate_bucket_take(&b, 2, 600000), 1);
    CHECK_EQ(gate_bucket_take(&b, 1, 600000), 0);
}

static void test_clock_going_backwards(void)
{
    gate_bucket b;
    gate_bucket_init(&b, 1, 1, 1000);
    gate_bucket_take(&b, 1, 1000);
    CHECK_EQ(gate_bucket_take(&b, 1, 10), 0);
}

static void test_retry_after(void)
{
    gate_bucket b;
    gate_bucket_init(&b, 1, 2, 0);
    gate_bucket_take(&b, 1, 0);
    CHECK_EQ(gate_bucket_retry_after_ms(&b, 1), 500);
    gate_bucket z;
    gate_bucket_init(&z, 1, 0, 0);
    gate_bucket_take(&z, 1, 0);
    CHECK_EQ(gate_bucket_retry_after_ms(&z, 1), -1);
    CHECK_EQ(gate_bucket_retry_after_ms(&b, 0), GATE_ERR_ARG);
}

static void test_validation_and_layout(void)
{
    gate_bucket b;
    CHECK_EQ(gate_bucket_init(&b, 0, 1, 0), GATE_ERR_ARG);
    CHECK_EQ(gate_bucket_init(&b, 1, -1, 0), GATE_ERR_ARG);
    CHECK_EQ(gate_bucket_init(NULL, 1, 1, 0), GATE_ERR_ARG);
    gate_bucket_init(&b, 1, 1, 0);
    CHECK_EQ(gate_bucket_take(&b, 0, 0), GATE_ERR_ARG);
    CHECK_EQ(gate_sizeof_bucket(), 32);
}

int main(void)
{
    test_burst_then_deny();
    test_refill_over_time();
    test_fractions_accumulate();
    test_capacity_caps_refill();
    test_clock_going_backwards();
    test_retry_after();
    test_validation_and_layout();
    CHECK_DONE();
}
