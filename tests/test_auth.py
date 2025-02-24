import unittest

from gatekit import auth, rules


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.store = auth.KeyStore([auth.Client("acme", 2, auth.digest("secret-a"), issued_day=10),
                                    auth.Client("hobby", 1, auth.digest("secret-h"))])

    def test_known_and_unknown_keys(self):
        self.assertEqual(self.store.authenticate("secret-a").name, "acme")
        self.assertIsNone(self.store.authenticate("wrong"))
        self.assertIsNone(self.store.authenticate(None))
        self.assertIsNone(self.store.authenticate(""))

    def test_keys_are_not_stored_in_clear(self):
        self.assertNotIn("secret-a", repr(self.store._clients))

    def test_expiry_follows_policy(self):
        client = self.store.authenticate("secret-a")
        horizon = rules.jwt_ttl_s(2) // 86400 + rules.key_rotation_days(2)
        self.assertFalse(self.store.expired(client, 10 + horizon))
        self.assertTrue(self.store.expired(client, 10 + horizon + 1))
