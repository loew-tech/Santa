import unittest
from santas_bag.interval import *


class TestIntervals(unittest.TestCase):

    def test_overlaps(self):
        # Basic overlap
        self.assertTrue(overlaps((1, 5), (3, 7)))
        # Contained
        self.assertTrue(overlaps((1, 10), (2, 5)))
        # No overlap
        self.assertFalse(overlaps((1, 2), (3, 4)))
        # Touching at boundary (usually considered overlap)
        self.assertTrue(overlaps((1, 2), (2, 3)))

    def test_contains(self):
        self.assertTrue(contains((1, 10), (2, 5)))
        self.assertFalse(contains((2, 5), (1, 10)))
        # Identity
        self.assertTrue(contains((1, 5), (1, 5)))

    def test_merge(self):
        self.assertEqual((1, 7), merge((1, 5), (3, 7)))
        self.assertEqual(None, merge((1, 2), (3, 4)))

    def test_merge_intervals(self):
        # Standard case
        data = [(1, 3), (2, 6), (8, 10), (15, 18)]
        expected = [(1, 6), (8, 10), (15, 18)]
        self.assertEqual(expected, merge_intervals(data))

        # Test adjacency logic (+1 behavior)
        data_adj = [(1, 2), (3, 4)]
        # Your current logic merges these because of 'last_end + 1'
        self.assertEqual([(1, 4)], merge_intervals(data_adj))

        # Empty list
        self.assertEqual([], merge_intervals([]))

    def test_find_interval_middle(self):
        intervals = [(1, 5), (10, 15), (20, 25)]
        self.assertEqual((10, 15), find_interval(intervals, 12))

    def test_find_interval_start(self):
        intervals = [(1, 5), (10, 15), (20, 25)]
        self.assertEqual((1, 5), find_interval(intervals, 1))

    def test_find_interval_end(self):
        intervals = [(1, 5), (10, 15), (20, 25)]
        self.assertEqual((20, 25), find_interval(intervals, 25))

    def test_find_interval_not_found(self):
        intervals = [(1, 5), (10, 15), (20, 25)]
        self.assertEqual(None, find_interval(intervals, 7))

    def test_find_interval_empty(self):
        self.assertEqual(None, find_interval([], 10))

    def test_find_interval_single(self):
        intervals = [(5, 10)]
        self.assertEqual((5, 10), find_interval(intervals, 7))
        self.assertEqual(None, find_interval(intervals, 1))


if __name__ == '__main__':
    unittest.main()