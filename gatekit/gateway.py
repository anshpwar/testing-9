"""Request handling: parse (C) -> authenticate -> rate limit (C) -> route -> upstream."""
from . import native, rules
from .quota import Limiter
from .resilience import CircuitBreaker, ResponseCache


class Gateway:
    def __init__(self, router, keystore, upstreams):
        self.router, self.keys, self.upstreams = router, keystore, upstreams
        self.limiter, self.cache = Limiter(), ResponseCache()
        self.breakers = {}

    def handle(self, raw, now_ms):
        """Return (status, headers, body). `raw` is the full request head (+ body)."""
        try:
            req, consumed = native.parse_request(raw)
        except native.ParseError as exc:
            return 400, {}, str(exc).encode()
        if req is None:
            return 400, {}, b"incomplete request"
        client = self.keys.authenticate(native.header(raw, "x-api-key"))
        if client is None:
            return 401, {}, b"missing or unknown API key"
        if req["header_count"] > rules.max_headers(client.plan_tier):
            return 431, {}, b"too many headers"
        if req["content_length"] > rules.max_body_kb(client.plan_tier) * 1024:
            return 413, {}, b"body too large"
        allowed, retry_ms = self.limiter.check(client, now_ms)
        if not allowed:
            return 429, {"Retry-After": str((retry_ms + 999) // 1000)}, b"rate limit exceeded"
        route, info = self.router.resolve(req["method"], req["path"])
        if route is None:
            return info, {}, b"no route" if info == 404 else b"method not allowed"
        now_s = now_ms // 1000
        cache_key = (route.upstream, req["path"])
        if req["method"] == "GET":
            hit = self.cache.get(cache_key, now_s)
            if hit is not None:
                return 200, {"X-Cache": "hit"}, hit
        breaker = self.breakers.setdefault(route.upstream, CircuitBreaker())
        if not breaker.allow(now_s):
            return 503, {}, b"upstream circuit open"
        try:
            body = self.upstreams[route.upstream](req, info)
            breaker.record(True, now_s)
        except Exception:  # an upstream may fail in any way; the breaker counts it
            breaker.record(False, now_s)
            return 502, {}, b"upstream failure"
        if req["method"] == "GET":
            self.cache.put(cache_key, body, now_s)
        return 200, {"X-Cache": "miss"}, body
