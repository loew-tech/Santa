import unittest
from santas_bag.search import *


class TestSearchAlgorithms(unittest.TestCase):

    def setUp(self):
        # A simple graph: 0 -> 1 -> 2 -> 3
        #                   \-> 4 -> 3
        self.graph = {0: [1, 4], 1: [2], 2: [3], 4: [3], 3: []}

    @staticmethod
    def get_neighbors(node, search_space, *args, **kwargs):
        return search_space.get(node, [])

    @staticmethod
    def make_is_terminal(target_node):
        return lambda node, search_space, *args, **kwargs: node == target_node

    def test_bfs_shortest_path(self):
        is_terminal = self.make_is_terminal(3)
        result, steps = bfs(0, self.graph, is_terminal, self.get_neighbors)
        self.assertEqual(result, 3)
        self.assertEqual(steps, 2)

    def test_bfs_start_is_terminal(self):
        is_terminal = self.make_is_terminal(0)
        result, steps = bfs(0, self.graph, is_terminal, self.get_neighbors)
        self.assertEqual(result, 0)
        self.assertEqual(steps, 0)

    def test_dfs_start_is_terminal(self):
        is_terminal = self.make_is_terminal(0)
        result, steps = dfs(0, self.graph, is_terminal, self.get_neighbors)
        self.assertEqual(result, 0)
        self.assertEqual(steps, 0)

    def test_dfs_finds_path(self):
        is_terminal = self.make_is_terminal(3)
        result, steps = dfs(0, self.graph, is_terminal, self.get_neighbors)
        self.assertEqual(result, 3)
        self.assertEqual(steps, 2)

    def test_no_path(self):
        is_terminal = self.make_is_terminal(99)
        result, steps = bfs(0, self.graph, is_terminal, self.get_neighbors)
        self.assertIsNone(result)
        self.assertEqual(steps, float('inf'))

    def test_a_star_shortest_path(self):
        is_terminal = self.make_is_terminal(3)
        # Manhattan-style heuristic: simple absolute difference distance estimate
        heuristic = lambda node, space: abs(3 - node)
        result, steps = a_star(0, self.graph, is_terminal, self.get_neighbors, heuristic)
        self.assertEqual(result, 3)
        self.assertEqual(steps, 2)

    def test_a_star_start_is_terminal(self):
        # Start at 0, terminal is 0.
        # A* needs a heuristic; 0 distance is always 0.
        is_terminal = self.make_is_terminal(0)
        heuristic = lambda node, space: 0
        result, steps = a_star(0, self.graph, is_terminal, self.get_neighbors, heuristic)
        self.assertEqual(result, 0)
        self.assertEqual(steps, 0)

    def test_get_state_pruning(self):
        """Verify that get_state correctly prunes visited nodes."""
        graph = {0: [1, 2], 1: [3], 2: [3], 3: []}
        is_terminal = self.make_is_terminal(3)

        # Mapping everything to 'X' means once 1 is visited, the state 'X' is blocked.
        # BFS will find 1, then fail to find 2 because state 'X' is already in visited.
        # get_state = lambda n: n

        result, steps = bfs(0, graph, is_terminal, self.get_neighbors)
        self.assertEqual(result, 3)
        self.assertEqual(steps, 2)

    def test_args_and_kwargs_passing(self):
        """Verify that *args and **kwargs pass transparently through the engine."""

        def get_neighbors_with_modifier(node, search_space, *args, **kwargs):
            neighbors = search_space.get(node, [])
            if kwargs.get('reverse'):
                return list(reversed(neighbors))
            return neighbors

        is_terminal = self.make_is_terminal(3)

        # Pass reverse=True as a kwarg through BFS to the neighbor generator
        result, steps = bfs(0, self.graph, is_terminal, get_neighbors_with_modifier, reverse=True)
        self.assertEqual(result, 3)

    def test_dijkstra_weighted_path(self):
        """
        Verify Dijkstra finds the shortest path by weight, not just hop count.
        Graph:
        0 -> 1 (weight 1)
        0 -> 2 (weight 10)
        1 -> 2 (weight 1)
        Path 0-2 (weight 10) vs 0-1-2 (weight 2)
        """
        graph = {
            0: [(1, 1), (2, 10)],
            1: [(2, 1)],
            2: []
        }

        # We need a modified neighbor getter that expects weighted tuples
        def get_weighted_neighbors(node, search_space, *args, **kwargs):
            return search_space.get(node, [])

        is_terminal = self.make_is_terminal(2)

        result, steps = dijkstra(0, graph, is_terminal, get_weighted_neighbors)

        self.assertEqual(result, 2)
        self.assertEqual(steps, 2)  # 0->1 (1) + 1->2 (1) = 2


if __name__ == '__main__':
    unittest.main()