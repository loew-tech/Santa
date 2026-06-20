import unittest

from santas_bag.parse import *

class TestParse(unittest.TestCase):

    def test_ints(self):
        self.assertEqual([10, 20, 30], ints("10, 20, 30"))
        self.assertEqual([-5, 100], ints("The values are -5 and 100"))
        self.assertEqual([], ints("No numbers here"))

    def test_nums(self):
        self.assertEqual([3.14, 10.0], nums("3.14 and 10"))
        self.assertEqual([-0.5, 1.5], nums("Negative -0.5 and positive 1.5"))

    def test_range_inclusive(self):
        r = range_("1 to 5", inclusive=True)
        self.assertEqual([1, 2, 3, 4, 5], list(r))

    def test_range_exclusive(self):
        r = range_("1 to 5", inclusive=False)
        self.assertEqual([1, 2, 3, 4], list(r))

    def test_range_error(self):
        with self.assertRaises(ValueError):
            range_("Just one number 5")

    def test_interval_exclusive(self):
        r = interval_tuple("1 to 5")
        self.assertEqual(1, r[0])
        self.assertEqual(5, r[1])

    def test_interval_error(self):
        with self.assertRaises(ValueError):
            interval_tuple("Just one number 5")

if __name__ == '__main__':
    unittest.main()
