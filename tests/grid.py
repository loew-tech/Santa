import unittest

from santas_bag.grid import *

class TestGrid(unittest.TestCase):

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
        self.all_paths_grid = [
            [2, 0, 3],
            [0, 1, 0],
            [0, 0, 3]
        ]
        self.impassable = {1}

    def test_inbounds(self):
        self.assertTrue(inbounds(self.sample_grid, 0, 0))
        self.assertTrue(inbounds(self.sample_grid, 1, 2))
        self.assertFalse(inbounds(self.sample_grid, -1, 0))
        self.assertFalse(inbounds(self.sample_grid, 0, 3))
        self.assertFalse(inbounds(self.sample_grid, 2, 0))

    def test_get_inbounds(self):
        check = get_inbounds(self.sample_grid)
        self.assertTrue(check(0, 0))
        self.assertFalse(check(5, 5))

    def test_grid_to_dict(self):
        expected = {
            (0, 0): 1, (0, 1): 2, (0, 2): 3,
            (1, 0): 4, (1, 1): 5, (1, 2): 6
        }
        self.assertEqual(expected, grid_to_dict(self.sample_grid))

    def test_transform_transpose_grid(self):
        expected = [
            [1, 4],
            [2, 5],
            [3, 6]
        ]
        self.assertEqual(expected, transform_grid(self.sample_grid, 'transpose'))

    def test_transform_h_flip(self):
        # h_flip is horizontal (left-to-right)
        expected = [
            [3, 2, 1],
            [6, 5, 4]
        ]
        self.assertEqual(expected, transform_grid(self.sample_grid, 'h_flip'))
        self.assertEqual(flip_horizontal(self.sample_grid), transform_grid(self.sample_grid, 'h_flip'))

    def test_transform_v_flip(self):
        expected = [
            [4, 5, 6],
            [1, 2, 3]
        ]
        self.assertEqual(expected, transform_grid(self.sample_grid, 'v_flip'))

    def test_transform_rot90(self):
        # Using sample_grid [[1, 2, 3], [4, 5, 6]]
        # Row 1 becomes col 1 (reversed), Row 2 becomes col 2 (reversed)
        expected = [
            [4, 1],
            [5, 2],
            [6, 3]
        ]
        self.assertEqual(expected, transform_grid(self.sample_grid, 'rot90'))
        # Ensure it matches your legacy rotate_clockwise function
        self.assertEqual(rotate_clockwise(self.sample_grid), transform_grid(self.sample_grid, 'rot90'))

    def test_transform_rot180(self):
        # 180 degrees is equivalent to reversing rows and columns
        expected = [
            [6, 5, 4],
            [3, 2, 1]
        ]
        self.assertEqual(expected, transform_grid(self.sample_grid, 'rot180'))

    def test_transform_rot270(self):
        # 270 degrees clockwise (or 90 counter-clockwise)
        expected = [
            [3, 6],
            [2, 5],
            [1, 4]
        ]
        self.assertEqual(expected, transform_grid(self.sample_grid, 'rot270'))

    def test_transform_invalid_mode(self):
        with self.assertRaises(ValueError):
            transform_grid(self.sample_grid, 'invalid_mode')

    def test_neighbors4(self):
        self.assertEqual(sorted([(0, 0), (0, 2), (1, 1)]), sorted(neighbors4(0, 1, self.sample_grid)))
        self.assertEqual(sorted([(0, 1), (1, 0)]), sorted(neighbors4(0, 0, self.sample_grid)))

    def test_neighbors8(self):
        expected = [(0, 0), (0, 2), (1, 0), (1, 1), (1, 2)]
        self.assertEqual(sorted(expected), sorted(neighbors8(0, 1, self.sample_grid)))
        self.assertEqual(sorted([(0, 1), (1, 0), (1, 1)]), sorted(neighbors8(0, 0, self.sample_grid)))

    def test_empty_grid(self):
        empty = []
        self.assertFalse(inbounds(empty, 0, 0))
        self.assertEqual({}, grid_to_dict(empty))
        self.assertEqual([], transpose_grid(empty))

    def test_taxi_distance(self):
        self.assertEqual(7, taxi_distance(0, 0, 3, 4))
        self.assertEqual(0, taxi_distance(1, 1, 1, 1))

    def test_rotate_clockwise(self):
        expected = [[4, 1], [5, 2], [6, 3]]
        self.assertEqual(expected, rotate_clockwise(self.sample_grid))

    def test_flip_horizontal(self):
        expected = [[3, 2, 1], [6, 5, 4]]
        self.assertEqual(expected, flip_horizontal(self.sample_grid))

    def test_find_all_in_grid(self):
        grid = [['A', 'B'], ['A', 'C']]
        self.assertEqual([(0, 0), (1, 0)], find_all_in_grid(grid, 'A'))
        self.assertEqual([], find_all_in_grid(grid, 'Z'))

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
        self.assertTrue(is_enclosed(grid, perimeter, 1, 1))

        # (0, 0) is ON the perimeter, so it returns False per your function's
        # first line: if (y, x) in perimeter: return False
        self.assertFalse(is_enclosed(grid, perimeter, 0, 0))

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
        self.assertEqual(1, area(loop))

    def test_grid_bfs_from_point(self):
        # BFS should find the shortest path: (0,0) -> (0,1) -> (1,0) ... path is blocked
        # Actually, let's verify finding goal (2,2)
        goal_pos, steps = grid_bfs_from_point(self.search_grid, 0, 0, 3, self.impassable)
        self.assertEqual((2, 2), goal_pos)
        self.assertEqual(4, steps)  # Simple check for path existence

    def test_grid_bfs_from_value(self):
        # Starts at '2', which is (0,0)
        goal_pos, steps = grid_bfs_from_value(self.search_grid, 2, 3, self.impassable)
        self.assertEqual((2, 2), goal_pos)

    def test_grid_dfs_from_point(self):
        # DFS might take a longer path, but should still reach the goal
        goal_pos, steps = grid_dfs_from_point(self.search_grid, 0, 0, 3, self.impassable)
        self.assertEqual(3, self.search_grid[goal_pos[0]][goal_pos[1]])

    def test_grid_dfs_from_value(self):
        # Starts at '2', which is (0,0)
        goal_pos, steps = grid_dfs_from_value(self.search_grid, 2, 3, self.impassable)
        self.assertEqual((2, 2), goal_pos)

    def test_no_path_found(self):
        grid_with_wall = [
            [2, 1, 0],
            [1, 1, 0],
            [0, 0, 3]
        ]
        # Start at (0,0) is blocked by walls from (2,2)
        goal_pos, steps = grid_bfs_from_point(grid_with_wall, 0, 0, 3, {1})
        self.assertIsNone(goal_pos)
        self.assertEqual(float('inf'), steps)

    def test_grid_find_all_paths_from_point(self):
        # Starting at (0,0), there are paths to both 3s:
        # Path 1: (0,0) -> (0,1) -> (1,1) -> (2, 1) ->  [Goal]
        # Path 2: (0,0) -> (1,0) -> (2,0) -> (2,1) -> (2,2) [Goal]
        paths = grid_find_all_paths_from_point(self.all_paths_grid, 0, 0, 3, self.impassable)

        self.assertEqual(2, len(paths))

        # Verify specific path endpoints
        endpoints = [p[-1] for p in paths]
        self.assertIn((0, 2), endpoints)
        self.assertIn((2, 2), endpoints)

    def test_grid_find_all_paths_from_value(self):
        # Uses the '2' at (0,0) to start
        paths = grid_find_all_paths_from_value(self.all_paths_grid, 2, 3, self.impassable)
        self.assertEqual(2, len(paths))

    def test_no_paths(self):
        blocked_grid = [
            [2, 1, 3],
            [1, 1, 0],
            [0, 0, 0]
        ]
        paths = grid_find_all_paths_from_point(blocked_grid, 0, 0, 3, {1})
        self.assertEqual(0, len(paths))

    def test_cycle_prevention(self):
        # Ensure it doesn't get stuck in an infinite loop
        grid = [
            [2, 0],
            [0, 3]
        ]
        paths = grid_find_all_paths_from_point(grid, 0, 0, 3)
        # Should finish execution successfully
        self.assertTrue(len(paths) > 0)

    def test_grid_class(self):
        g = Grid(self.sample_grid, impassable={6})
        self.assertEqual(5, g[(1, 1)])
        self.assertTrue(g.is_inbounds(1, 2))
        self.assertFalse(g.is_inbounds(5, 5))
        self.assertTrue(g.is_valid(1, 1))
        self.assertFalse(g.is_valid(1, 2))


if __name__ == '__main__':
    unittest.main()
