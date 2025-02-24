import unittest

from gatekit import config, rules
from gatekit.gateway import Gateway

INI = """
[route:users]
pattern = /v1/users/{id}
upstream = users
methods = GET,PUT

[client:acme]
key = k-acme
tier = 2
"""


def request(path="/v1/users/7", key="k-acme", method="GET", extra=""):
    head = f"{method} {path} HTTP/1.1\r\nHost: h\r\n"
    if key:
        head += f"X-Api-Key: {key}\r\n"
    return (head + extra + "\r\n").encode()


class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        router, keys = config.load(INI)

        def users(req, params):
            self.calls.append(params["id"])
            return b'{"id": "%s"}' % params["id"].encode()

        self.gw = Gateway(router, keys, {"users": users})

    def test_authenticated_request_reaches_the_upstream(self):
        status, headers, body = self.gw.handle(request(), 0)
        self.assertEqual((status, body), (200, b'{"id": "7"}'))
        self.assertEqual(headers["X-Cache"], "miss")

    def test_auth_failures(self):
        self.assertEqual(self.gw.handle(request(key=None), 0)[0], 401)
        self.assertEqual(self.gw.handle(request(key="nope"), 0)[0], 401)

    def test_routing_failures(self):
        self.assertEqual(self.gw.handle(request("/nowhere"), 0)[0], 404)
        self.assertEqual(self.gw.handle(request(method="DELETE"), 0)[0], 405)

    def test_malformed_and_oversized_requests(self):
        self.assertEqual(self.gw.handle(b"garbage\r\n\r\n", 0)[0], 400)
        big = rules.max_body_kb(2) * 1024 + 1
        self.assertEqual(self.gw.handle(request(extra=f"Content-Length: {big}\r\n"), 0)[0], 413)

    def test_rate_limit_returns_429_with_retry_after(self):
        statuses = [self.gw.handle(request(f"/v1/users/{i}"), 0)[0] for i in range(2000)]
        self.assertIn(429, statuses)
        status, headers, _ = self.gw.handle(request("/v1/users/x"), 0)
        self.assertEqual(status, 429)
        self.assertGreaterEqual(int(headers["Retry-After"]), 1)

    def test_get_responses_are_cached_when_policy_allows(self):
        self.gw.handle(request(), 0)
        status, headers, _ = self.gw.handle(request(), 1000)
        if rules.cache_ttl_s(1) > 1:
            self.assertEqual(headers.get("X-Cache"), "hit")
            self.assertEqual(self.calls, ["7"])

    def test_failing_upstream_opens_the_breaker(self):
        router, keys = config.load(INI)
        gw = Gateway(router, keys, {"users": lambda req, params: 1 / 0})
        codes = [gw.handle(request(f"/v1/users/{i}"), i * 1000)[0] for i in range(8)]
        self.assertEqual(codes[:5], [502] * 5)
        self.assertIn(503, codes[5:])
