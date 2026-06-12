import unittest

from santas_bag.grid import *

class TestGridHelpers(unittest.TestCase):

    def setUp(self):
        self.sample_grid = [
            [1, 2, 3],
            [4, 5, 6]
        ]

    def test_inbounds(self):
        self.assertTrue(inbounds(0, 0, self.sample_grid))
        self.assertTrue(inbounds(1, 2, self.sample_grid))
        self.assertFalse(inbounds(-1, 0, self.sample_grid))
        self.assertFalse(inbounds(0, 3, self.sample_grid))
        self.assertFalse(inbounds(2, 0, self.sample_grid))

    def test_get_inbounds(self):
        check = get_inbounds(self.sample_grid)
        self.assertTrue(check(0, 0))
        self.assertFalse(check(5, 5))

    def test_grid_to_dict(self):
        expected = {
            (0, 0): 1, (0, 1): 2, (0, 2): 3,
            (1, 0): 4, (1, 1): 5, (1, 2): 6
        }
        self.assertEqual(grid_to_dict(self.sample_grid), expected)

    def test_transpose_grid(self):
        expected = [
            [1, 4],
            [2, 5],
            [3, 6]
        ]
        self.assertEqual(transpose_grid(self.sample_grid), expected)

    def test_neighbors4(self):
        self.assertEqual(sorted(neighbors4(0, 1, self.sample_grid)), sorted([(0, 0), (0, 2), (1, 1)]))
        self.assertEqual(sorted(neighbors4(0, 0, self.sample_grid)), sorted([(0, 1), (1, 0)]))

    def test_neighbors8(self):
        expected = [(0, 0), (0, 2), (1, 0), (1, 1), (1, 2)]
        self.assertEqual(sorted(neighbors8(0, 1, self.sample_grid)), sorted(expected))
        self.assertEqual(sorted(neighbors8(0, 0, self.sample_grid)), sorted([(0, 1), (1, 0), (1, 1)]))

    def test_empty_grid(self):
        empty = []
        self.assertFalse(inbounds(0, 0, empty))
        self.assertEqual(grid_to_dict(empty), {})
        self.assertEqual(transpose_grid(empty), [])


if __name__ == '__main__':
    unittest.main()
