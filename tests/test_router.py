import unittest

from gatekit.router import Route, Router


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.router = Router([
            Route("/v1/users/{id}", "users", ("GET", "PUT")),
            Route("/v1/users/me", "me", ("GET",)),
            Route("/v1/orders", "orders", ("GET", "POST")),
        ])

    def test_param_extraction(self):
        route, params = self.router.resolve("GET", "/v1/users/42?x=1")
        self.assertEqual((route.upstream, params), ("users", {"id": "42"}))

    def test_literal_route_beats_parameter_route(self):
        route, _ = self.router.resolve("GET", "/v1/users/me")
        self.assertEqual(route.upstream, "me")

    def test_404_and_405(self):
        self.assertEqual(self.router.resolve("GET", "/nope"), (None, 404))
        self.assertEqual(self.router.resolve("DELETE", "/v1/orders"), (None, 405))

    def test_trailing_slash_is_ignored(self):
        self.assertIsNotNone(self.router.resolve("GET", "/v1/orders/")[0])
