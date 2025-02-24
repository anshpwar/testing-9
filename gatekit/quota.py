"""Per-client rate limiting with C token buckets sized by plan tier."""
from . import rules
from .native import Bucket


def bucket_for(plan_tier, now_ms):
    rps = max(1, rules.rate_limit_rps(plan_tier))
    burst = max(rps, rules.burst_capacity(plan_tier), 1)
    return Bucket(burst, rps, now_ms)


class Limiter:
    def __init__(self):
        self._buckets = {}

    def check(self, client, now_ms):
        """Return (allowed, retry_after_ms)."""
        bucket = self._buckets.get(client.name)
        if bucket is None:
            bucket = self._buckets[client.name] = bucket_for(client.plan_tier, now_ms)
        if bucket.take(now_ms):
            return True, 0
        return False, bucket.retry_after_ms()


def monthly_allowance(plan_tier):
    return rules.quota_monthly_calls(plan_tier)
