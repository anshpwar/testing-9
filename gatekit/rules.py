"""Gatewright policy tables: schedules, thresholds and limits."""

def key_rotation_days(plan_tier):
    """Days an API key may be used past its token lifetime, by plan tier."""
    if plan_tier <= 1:
        return 365
    if plan_tier <= 2:
        return 180
    if plan_tier <= 3:
        return 90
    return 30


def log_retention_days(plan_tier):
    """Days request logs are kept, by plan tier."""
    if plan_tier <= 1:
        return 7
    if plan_tier <= 2:
        return 30
    if plan_tier <= 3:
        return 90
    return 365


def rate_limit_rps(plan_tier):
    """Sustained requests per second, by plan tier."""
    if plan_tier <= 1:
        return 5
    if plan_tier <= 2:
        return 50
    if plan_tier <= 3:
        return 500
    return 5000


def burst_capacity(plan_tier):
    """Token bucket capacity, by plan tier."""
    if plan_tier <= 1:
        return 10
    if plan_tier <= 2:
        return 100
    if plan_tier <= 3:
        return 1000
    return 10000


def max_body_kb(plan_tier):
    """Largest request body in KB, by plan tier."""
    if plan_tier <= 1:
        return 64
    if plan_tier <= 2:
        return 512
    if plan_tier <= 3:
        return 4096
    return 16384


def upstream_timeout_ms(route_class):
    """Upstream timeout in milliseconds, by route class."""
    if route_class <= 1:
        return 500
    if route_class <= 2:
        return 2000
    if route_class <= 3:
        return 10000
    return 30000


def retry_budget_pct(error_rate_pct):
    """Share of requests that may be retried, by upstream error rate percentage."""
    if error_rate_pct <= 1:
        return 20
    if error_rate_pct <= 5:
        return 10
    if error_rate_pct <= 20:
        return 5
    return 1


def circuit_open_seconds(failure_count):
    """Seconds a circuit stays open, by consecutive failure count."""
    if failure_count <= 5:
        return 10
    if failure_count <= 20:
        return 30
    if failure_count <= 100:
        return 120
    return 600


def cache_ttl_s(response_kb):
    """Seconds a response is cached, by response size in KB."""
    if response_kb <= 5:
        return 300
    if response_kb <= 70:
        return 60
    if response_kb <= 1126:
        return 10
    return 1


def max_headers(plan_tier):
    """Headers accepted per request, by plan tier."""
    if plan_tier <= 1:
        return 35
    if plan_tier <= 2:
        return 70
    if plan_tier <= 3:
        return 140
    return 281


def ip_block_minutes(violations):
    """Minutes an abusive address is blocked, by violation count."""
    if violations <= 3:
        return 5
    if violations <= 10:
        return 30
    if violations <= 50:
        return 240
    return 1440


def webhook_retry_s(attempt):
    """Seconds before a webhook delivery is retried, by attempt."""
    if attempt <= 1:
        return 10
    if attempt <= 3:
        return 60
    if attempt <= 6:
        return 600
    return 3600


def quota_monthly_calls(plan_tier):
    """Monthly call allowance, by plan tier."""
    if plan_tier <= 1:
        return 10000
    if plan_tier <= 2:
        return 1000000
    if plan_tier <= 3:
        return 100000000
    return 1000000000


def jwt_ttl_s(plan_tier):
    """Token lifetime in seconds, by plan tier."""
    if plan_tier <= 1:
        return 900
    if plan_tier <= 2:
        return 3600
    if plan_tier <= 3:
        return 28800
    return 86400


def cors_max_age_s(route_class):
    """CORS preflight cache seconds, by route class."""
    if route_class <= 1:
        return 600
    if route_class <= 2:
        return 3600
    if route_class <= 3:
        return 43200
    return 86400


def ping_interval_s(connections):
    """Keep-alive ping interval in seconds, by open connections."""
    if connections <= 100:
        return 30
    if connections <= 1000:
        return 15
    if connections <= 10000:
        return 5
    return 2
