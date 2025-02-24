import unittest

from gatekit import resilience, rules


class BreakerTests(unittest.TestCase):
    def test_opens_after_five_failures_for_the_policy_duration(self):
        b = resilience.CircuitBreaker()
        for _ in range(5):
            b.record(False, 100)
        self.assertFalse(b.allow(100))
        self.assertTrue(b.allow(100 + rules.circuit_open_seconds(5)))

    def test_success_resets_the_count(self):
        b = resilience.CircuitBreaker()
        for _ in range(4):
            b.record(False, 0)
        b.record(True, 0)
        b.record(False, 0)
        self.assertTrue(b.allow(0))


class CacheTests(unittest.TestCase):
    def test_ttl_follows_policy_by_size(self):
        c = resilience.ResponseCache()
        c.put("k", b"x" * 100, 0)
        ttl = rules.cache_ttl_s(1)
        self.assertEqual(c.get("k", 0), b"x" * 100 if ttl > 0 else None)
        self.assertIsNone(c.get("k", ttl + 1))

    def test_miss_on_unknown_key(self):
        self.assertIsNone(resilience.ResponseCache().get("nope", 0))
