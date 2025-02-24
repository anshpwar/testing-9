import unittest

from gatekit import auth, quota, rules


class QuotaTests(unittest.TestCase):
    def client(self, tier):
        return auth.Client(f"c{tier}", tier, auth.digest("k"))

    def test_burst_matches_plan(self):
        lim = quota.Limiter()
        c = self.client(1)
        burst = max(max(1, rules.rate_limit_rps(1)), rules.burst_capacity(1), 1)
        allowed = sum(1 for _ in range(burst + 5) if lim.check(c, 0)[0])
        self.assertEqual(allowed, burst)

    def test_denied_requests_report_retry_after(self):
        lim = quota.Limiter()
        c = self.client(1)
        while lim.check(c, 0)[0]:
            pass
        ok, retry = lim.check(c, 0)
        self.assertFalse(ok)
        self.assertGreater(retry, 0)

    def test_clients_have_separate_buckets(self):
        lim = quota.Limiter()
        a, b = self.client(1), self.client(2)
        while lim.check(a, 0)[0]:
            pass
        self.assertTrue(lim.check(b, 0)[0])

    def test_monthly_allowance(self):
        self.assertEqual(quota.monthly_allowance(3), rules.quota_monthly_calls(3))
