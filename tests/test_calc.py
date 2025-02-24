import unittest

from gatekit import calc


class CalcTests(unittest.TestCase):
    def test_combined_charge(self):
        self.assertEqual(calc.combined_charge(0), 372)
        self.assertEqual(calc.combined_charge(1), 372)
        self.assertEqual(calc.combined_charge(2), 210)
        self.assertEqual(calc.combined_charge(3), 180)
