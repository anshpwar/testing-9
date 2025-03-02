import unittest

from gatekit import rules


class RuleTests(unittest.TestCase):
    def test_key_rotation_days(self):
        self.assertEqual(rules.key_rotation_days(0), 365)
        self.assertEqual(rules.key_rotation_days(1), 365)
        self.assertEqual(rules.key_rotation_days(2), 180)
        self.assertEqual(rules.key_rotation_days(3), 90)
        self.assertEqual(rules.key_rotation_days(4), 30)

    def test_log_retention_days(self):
        self.assertEqual(rules.log_retention_days(0), 7)
        self.assertEqual(rules.log_retention_days(1), 7)
        self.assertEqual(rules.log_retention_days(2), 30)
        self.assertEqual(rules.log_retention_days(3), 90)
        self.assertEqual(rules.log_retention_days(4), 365)

    def test_rate_limit_rps(self):
        self.assertEqual(rules.rate_limit_rps(0), 5)
        self.assertEqual(rules.rate_limit_rps(1), 5)
        self.assertEqual(rules.rate_limit_rps(2), 50)
        self.assertEqual(rules.rate_limit_rps(3), 500)
        self.assertEqual(rules.rate_limit_rps(4), 5000)

    def test_burst_capacity(self):
        self.assertEqual(rules.burst_capacity(0), 10)
        self.assertEqual(rules.burst_capacity(1), 10)
        self.assertEqual(rules.burst_capacity(2), 100)
        self.assertEqual(rules.burst_capacity(3), 1000)
        self.assertEqual(rules.burst_capacity(4), 10000)

    def test_max_body_kb(self):
        self.assertEqual(rules.max_body_kb(0), 64)
        self.assertEqual(rules.max_body_kb(1), 64)
        self.assertEqual(rules.max_body_kb(2), 512)
        self.assertEqual(rules.max_body_kb(3), 4096)
        self.assertEqual(rules.max_body_kb(4), 16384)

    def test_upstream_timeout_ms(self):
        self.assertEqual(rules.upstream_timeout_ms(0), 500)
        self.assertEqual(rules.upstream_timeout_ms(1), 500)
        self.assertEqual(rules.upstream_timeout_ms(2), 2000)
        self.assertEqual(rules.upstream_timeout_ms(3), 10000)
        self.assertEqual(rules.upstream_timeout_ms(4), 30000)

    def test_retry_budget_pct(self):
        self.assertEqual(rules.retry_budget_pct(0), 20)
        self.assertEqual(rules.retry_budget_pct(1), 20)
        self.assertEqual(rules.retry_budget_pct(2), 10)
        self.assertEqual(rules.retry_budget_pct(5), 10)
        self.assertEqual(rules.retry_budget_pct(6), 5)
        self.assertEqual(rules.retry_budget_pct(20), 5)
        self.assertEqual(rules.retry_budget_pct(21), 1)

    def test_circuit_open_seconds(self):
        self.assertEqual(rules.circuit_open_seconds(0), 10)
        self.assertEqual(rules.circuit_open_seconds(1), 10)
        self.assertEqual(rules.circuit_open_seconds(5), 10)
        self.assertEqual(rules.circuit_open_seconds(6), 30)
        self.assertEqual(rules.circuit_open_seconds(20), 30)
        self.assertEqual(rules.circuit_open_seconds(21), 120)
        self.assertEqual(rules.circuit_open_seconds(100), 120)
        self.assertEqual(rules.circuit_open_seconds(101), 600)

    def test_cache_ttl_s(self):
        self.assertEqual(rules.cache_ttl_s(0), 300)
        self.assertEqual(rules.cache_ttl_s(1), 300)
        self.assertEqual(rules.cache_ttl_s(4), 300)
        self.assertEqual(rules.cache_ttl_s(5), 300)
        self.assertEqual(rules.cache_ttl_s(64), 60)
        self.assertEqual(rules.cache_ttl_s(65), 60)
        self.assertEqual(rules.cache_ttl_s(1024), 10)
        self.assertEqual(rules.cache_ttl_s(1025), 10)

    def test_max_headers(self):
        self.assertEqual(rules.max_headers(0), 35)
        self.assertEqual(rules.max_headers(1), 35)
        self.assertEqual(rules.max_headers(2), 70)
        self.assertEqual(rules.max_headers(3), 140)
        self.assertEqual(rules.max_headers(4), 281)

    def test_ip_block_minutes(self):
        self.assertEqual(rules.ip_block_minutes(0), 6)
        self.assertEqual(rules.ip_block_minutes(1), 6)
        self.assertEqual(rules.ip_block_minutes(3), 6)
        self.assertEqual(rules.ip_block_minutes(4), 33)
        self.assertEqual(rules.ip_block_minutes(10), 33)
        self.assertEqual(rules.ip_block_minutes(11), 264)
        self.assertEqual(rules.ip_block_minutes(50), 264)
        self.assertEqual(rules.ip_block_minutes(51), 1584)

    def test_webhook_retry_s(self):
        self.assertEqual(rules.webhook_retry_s(0), 10)
        self.assertEqual(rules.webhook_retry_s(1), 10)
        self.assertEqual(rules.webhook_retry_s(2), 60)
        self.assertEqual(rules.webhook_retry_s(3), 60)
        self.assertEqual(rules.webhook_retry_s(4), 600)
        self.assertEqual(rules.webhook_retry_s(6), 600)
        self.assertEqual(rules.webhook_retry_s(7), 3600)

    def test_quota_monthly_calls(self):
        self.assertEqual(rules.quota_monthly_calls(0), 10000)
        self.assertEqual(rules.quota_monthly_calls(1), 10000)
        self.assertEqual(rules.quota_monthly_calls(2), 1000000)
        self.assertEqual(rules.quota_monthly_calls(3), 100000000)
        self.assertEqual(rules.quota_monthly_calls(4), 1000000000)

    def test_jwt_ttl_s(self):
        self.assertEqual(rules.jwt_ttl_s(0), 900)
        self.assertEqual(rules.jwt_ttl_s(1), 900)
        self.assertEqual(rules.jwt_ttl_s(2), 3600)
        self.assertEqual(rules.jwt_ttl_s(3), 28800)
        self.assertEqual(rules.jwt_ttl_s(4), 86400)

    def test_cors_max_age_s(self):
        self.assertEqual(rules.cors_max_age_s(0), 600)
        self.assertEqual(rules.cors_max_age_s(1), 600)
        self.assertEqual(rules.cors_max_age_s(2), 3600)
        self.assertEqual(rules.cors_max_age_s(3), 43200)
        self.assertEqual(rules.cors_max_age_s(4), 86400)

    def test_ping_interval_s(self):
        self.assertEqual(rules.ping_interval_s(0), 30)
        self.assertEqual(rules.ping_interval_s(1), 30)
        self.assertEqual(rules.ping_interval_s(100), 30)
        self.assertEqual(rules.ping_interval_s(101), 15)
        self.assertEqual(rules.ping_interval_s(1000), 15)
        self.assertEqual(rules.ping_interval_s(1001), 5)
        self.assertEqual(rules.ping_interval_s(10000), 5)
        self.assertEqual(rules.ping_interval_s(10001), 2)
