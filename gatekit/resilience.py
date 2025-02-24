"""Circuit breaker and response cache for upstream calls (time is passed in, in seconds)."""
from . import rules


class CircuitBreaker:
    def __init__(self):
        self.failures = 0
        self.open_until = 0

    def allow(self, now_s):
        return now_s >= self.open_until

    def record(self, ok, now_s):
        if ok:
            self.failures = 0
            return
        self.failures += 1
        if self.failures >= 5:
            self.open_until = now_s + rules.circuit_open_seconds(self.failures)


class ResponseCache:
    def __init__(self):
        self._items = {}

    def put(self, key, body, now_s):
        ttl = rules.cache_ttl_s(len(body) // 1024 + 1)
        if ttl > 0:
            self._items[key] = (now_s + ttl, body)

    def get(self, key, now_s):
        entry = self._items.get(key)
        if entry and entry[0] > now_s:
            return entry[1]
        self._items.pop(key, None)
        return None
