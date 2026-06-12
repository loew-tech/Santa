import unittest

from santas_bag.search import bfs, dfs


class TestSearchAlgorithms(unittest.TestCase):

    def setUp(self):
        # A simple graph: 0 -> 1 -> 2 -> 3
        #                   \-> 4 -> 3
        self.graph = {0: [1, 4], 1: [2], 2: [3], 4: [3], 3: []}

    def get_neighbors(self, node, search_space, *args, **kwargs):
        # Neighbors are determined by looking up the current node in the search space
        return search_space.get(node, [])

    def make_is_terminal(self, target_node):
        # Factory function matching your design: target is enclosed in the lambda
        return lambda node, search_space, *args, **kwargs: node == target_node

    def test_bfs_shortest_path(self):
        # BFS should find 0 -> 4 -> 3 (2 steps) instead of 0 -> 1 -> 2 -> 3 (3 steps)
        is_terminal = self.make_is_terminal(3)

        result, steps = bfs(0, self.graph, is_terminal, self.get_neighbors)
        self.assertEqual(result, 3)
        self.assertEqual(steps, 2)

    def test_dfs_finds_path(self):
        # DFS follows the first branch it sees (LIFO stack behavior)
        is_terminal = self.make_is_terminal(3)

        result, steps = dfs(0, self.graph, is_terminal, self.get_neighbors)
        self.assertEqual(result, 3)
        # 0 -> 4 -> 3 is 3 steps
        self.assertEqual(steps, 2)

    def test_no_path(self):
        is_terminal = self.make_is_terminal(99)  # Node doesn't exist

        result, steps = bfs(0, self.graph, is_terminal, self.get_neighbors)
        self.assertIsNone(result)
        self.assertEqual(steps, float('inf'))

    def test_args_and_kwargs_passing(self):
        # Verification that *args and **kwargs still transparently pass through the engine
        def get_neighbors_with_modifier(node, search_space, *args, **kwargs):
            neighbors = search_space.get(node, [])
            if kwargs.get('reverse'):
                return list(reversed(neighbors))
            return neighbors

        is_terminal = self.make_is_terminal(3)

        # Pass reverse=True as a kwarg through BFS to the neighbor generator
        result, steps = bfs(0, self.graph, is_terminal, get_neighbors_with_modifier, reverse=True)
        self.assertEqual(result, 3)


if __name__ == '__main__':
    unittest.main()
