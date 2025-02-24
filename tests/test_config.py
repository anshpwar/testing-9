import pathlib
import unittest

from gatekit import cli, config

ROOT = pathlib.Path(__file__).resolve().parent.parent


class ConfigTests(unittest.TestCase):
    def test_shipped_config_loads(self):
        router, keys = config.load((ROOT / "config" / "gateway.ini").read_text())
        self.assertEqual(len(router.routes), 2)
        self.assertIsNotNone(keys.authenticate("demo-key-acme-not-a-secret"))

    def test_missing_fields_are_rejected(self):
        for text in ("[route:x]\npattern=/a\n", "[client:y]\ntier=1\n", "[bogus:z]\na=1\n"):
            with self.assertRaises(config.ConfigError):
                config.load(text)

    def test_cli_check(self):
        import io
        out = io.StringIO()
        self.assertEqual(cli.main(["check", str(ROOT / "config" / "gateway.ini")], out=out), 0)
        self.assertIn("2 routes, 2 clients", out.getvalue())
