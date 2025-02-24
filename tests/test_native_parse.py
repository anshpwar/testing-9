import ctypes
import unittest

from gatekit import native

GOOD = b"GET /v1/users/7 HTTP/1.1\r\nHost: api.example.invalid\r\nX-Api-Key: k1\r\nContent-Length: 5\r\n\r\nhello"


class ParseTests(unittest.TestCase):
    def test_parses_request_head(self):
        req, consumed = native.parse_request(GOOD)
        self.assertEqual((req["method"], req["path"], req["content_length"]), ("GET", "/v1/users/7", 5))
        self.assertEqual(consumed, len(GOOD) - 5)
        self.assertTrue(req["keep_alive"])

    def test_incomplete_head_returns_none(self):
        self.assertEqual(native.parse_request(b"GET / HTTP/1.1\r\nHost: x\r\n"), (None, 0))

    def test_errors_raise_with_codes(self):
        for raw, code in ((b"get / HTTP/1.1\r\n\r\n", native.ERR_SYNTAX), (b"GET / HTTP/2.0\r\n\r\n", native.ERR_SYNTAX)):
            with self.assertRaises(native.ParseError) as cm:
                native.parse_request(raw)
            self.assertEqual(cm.exception.code, code)

    def test_too_many_headers(self):
        raw = b"GET / HTTP/1.1\r\n" + b"".join(b"X-%d: v\r\n" % i for i in range(native.GATE_MAX_HEADERS + 1)) + b"\r\n"
        with self.assertRaises(native.ParseError) as cm:
            native.parse_request(raw)
        self.assertEqual(cm.exception.code, native.ERR_TOO_MANY)

    def test_header_lookup_is_case_insensitive(self):
        self.assertEqual(native.header(GOOD, "x-API-key"), "k1")
        self.assertIsNone(native.header(GOOD, "x-missing"))

    def test_struct_layouts_match_the_library(self):
        self.assertEqual(ctypes.sizeof(native.GateRequest), native.lib.gate_sizeof_request())
        self.assertEqual(ctypes.sizeof(native.GateBucket), native.lib.gate_sizeof_bucket())
