import unittest
from santas_bag.graph import topological_sort


class TestTopologicalSort(unittest.TestCase):

    def setUp(self):
        # A simple dependency graph:
        # 0 -> 1, 0 -> 2
        # 1 -> 3
        # 2 -> 3
        self.graph = {0: [1, 2], 1: [3], 2: [3], 3: []}
        self.nodes = [0, 1, 2, 3]

    def test_basic_topological_sort(self):
        """Standard DAG test where order must be [0, 1, 2, 3] or [0, 2, 1, 3]."""
        result = topological_sort(self.nodes, self.graph)
        # Verify length
        self.assertEqual(len(result), 4)

        # Verify dependencies (0 must come before 1 and 2, 1 and 2 before 3)
        self.assertTrue(result.index(0) < result.index(1))
        self.assertTrue(result.index(0) < result.index(2))
        self.assertTrue(result.index(1) < result.index(3))
        self.assertTrue(result.index(2) < result.index(3))

    def test_disconnected_components(self):
        """Tests that nodes with no dependencies are handled correctly."""
        graph = {0: [1], 1: [], 2: [3], 3: []}
        nodes = [0, 1, 2, 3]

        result = topological_sort(nodes, graph)

        self.assertEqual(len(result), 4)
        self.assertTrue(result.index(0) < result.index(1))
        self.assertTrue(result.index(2) < result.index(3))

    def test_single_node(self):
        """Edge case: Single node graph."""
        graph = {0: []}
        result = topological_sort([0], graph)
        self.assertEqual(result, [0])


if __name__ == '__main__':
    unittest.main()