import unittest

from santas_bag.grid import *

class TestGridHelpers(unittest.TestCase):

    def setUp(self):
        self.sample_grid = [
            [1, 2, 3],
            [4, 5, 6]
        ]

        self.search_grid = [
            [2, 0, 1],
            [1, 0, 0],
            [4, 1, 3]
        ]
        self.impassable = {1}

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

    def test_taxi_distance(self):
        self.assertEqual(taxi_distance(0, 0, 3, 4), 7)
        self.assertEqual(taxi_distance(1, 1, 1, 1), 0)

    def test_rotate_clockwise(self):
        expected = [[4, 1], [5, 2], [6, 3]]
        self.assertEqual(rotate_clockwise(self.sample_grid), expected)

    def test_flip_horizontal(self):
        expected = [[3, 2, 1], [6, 5, 4]]
        self.assertEqual(flip_horizontal(self.sample_grid), expected)

    def test_find_all_in_grid(self):
        grid = [['A', 'B'], ['A', 'C']]
        self.assertEqual(find_all_in_grid('A', grid), [(0, 0), (1, 0)])
        self.assertEqual(find_all_in_grid('Z', grid), [])

    def test_is_enclosed(self):
        # A proper closed loop: (1,1) is trapped inside
        grid = [
            ['|', '|', '|'],
            ['|', '.', '|'],
            ['|', '|', '|']
        ]
        # perimeter is now a complete box
        perimeter = {
            (0, 0), (0, 1), (0, 2),
            (1, 0), (1, 2),
            (2, 0), (2, 1), (2, 2)
        }

        # (1, 1) is inside
        self.assertTrue(is_enclosed(1, 1, grid, perimeter))

        # (0, 0) is ON the perimeter, so it returns False per your function's
        # first line: if (y, x) in perimeter: return False
        self.assertFalse(is_enclosed(0, 0, grid, perimeter))

    def test_get_is_enclosed(self):
        # A single pipe segment is not an enclosure.
        # To be "enclosed", the ray must be able to escape to the outside.
        grid = [
            ['.', '|', '.', '|', '.']
        ]
        # Here, index 2 is enclosed by walls at 1 and 3
        perimeter = {(0, 1), (0, 3)}
        enclosed_check = get_is_enclosed(grid, perimeter)

        # (0, 0) is outside: crosses 0 walls (Even) -> False
        self.assertFalse(enclosed_check(0, 0))

        # (0, 2) is inside: crosses 1 wall (Odd) -> True
        self.assertTrue(enclosed_check(0, 2))

        # (0, 4) is outside: crosses 2 walls (Even) -> False
        self.assertFalse(enclosed_check(0, 4)) # Outside

    def test_area_picks_theorem(self):
        # A 3x3 square loop has 8 boundary points
        # The points are (0,0), (0,1), (0,2), (1,2), (2,2), (2,1), (2,0), (1,0)
        loop = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0)]
        # I = Area - (B/2) + 1 => I = 4 - (8/2) + 1 = 1
        self.assertEqual(area(loop), 1)

    def test_grid_bfs_from_point(self):
        # BFS should find the shortest path: (0,0) -> (0,1) -> (1,0) ... path is blocked
        # Actually, let's verify finding goal (2,2)
        goal_pos, steps = grid_bfs_from_point(0, 0, 3, self.search_grid, self.impassable)
        self.assertEqual((2, 2), goal_pos)
        self.assertLess(steps, 10)  # Simple check for path existence

    def test_grid_bfs_from_value(self):
        # Starts at '2', which is (0,0)
        goal_pos, steps = grid_bfs_from_value(2, 3, self.search_grid, self.impassable)
        self.assertEqual(goal_pos, (2, 2))

    def test_grid_dfs_from_point(self):
        # DFS might take a longer path, but should still reach the goal
        goal_pos, steps = grid_dfs_from_point(0, 0, 3, self.search_grid, self.impassable)
        self.assertEqual(self.search_grid[goal_pos[0]][goal_pos[1]], 3)

    def test_grid_dfs_from_value(self):
        # Starts at '2', which is (0,0)
        goal_pos, steps = grid_dfs_from_value(2, 3, self.search_grid, self.impassable)
        self.assertEqual(goal_pos, (2, 2))

    def test_no_path_found(self):
        grid_with_wall = [
            [2, 1, 0],
            [1, 1, 0],
            [0, 0, 3]
        ]
        # Start at (0,0) is blocked by walls from (2,2)
        goal_pos, steps = grid_bfs_from_point(0, 0, 3, grid_with_wall, {1})
        self.assertIsNone(goal_pos)
        self.assertEqual(steps, float('inf'))

    def test_grid_class(self):
        g = Grid(self.sample_grid)
        self.assertEqual(g[(1, 1)], 5)
        self.assertTrue(g.is_inbounds(1, 2))
        self.assertFalse(g.is_inbounds(5, 5))

if __name__ == '__main__':
    unittest.main()
