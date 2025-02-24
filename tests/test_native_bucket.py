import unittest

from gatekit import native


class BucketTests(unittest.TestCase):
    def test_burst_then_refill(self):
        b = native.Bucket(2, 2, 0)
        self.assertTrue(b.take(0) and b.take(0))
        self.assertFalse(b.take(0))
        self.assertFalse(b.take(100))
        self.assertTrue(b.take(500))

    def test_retry_after(self):
        b = native.Bucket(1, 2, 0)
        b.take(0)
        self.assertEqual(b.retry_after_ms(), 500)
        never = native.Bucket(1, 0, 0)
        never.take(0)
        self.assertEqual(never.retry_after_ms(), -1)

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            native.Bucket(0, 1, 0)
        with self.assertRaises(ValueError):
            native.Bucket(1, 1, 0).take(0, cost=0)
