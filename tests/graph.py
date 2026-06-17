import unittest
from santas_bag.graph import *


class TestGraph(unittest.TestCase):

    def setUp(self):
        # A simple dependency graph:
        # 0 -> 1, 0 -> 2
        # 1 -> 3
        # 2 -> 3
        self.graph = {0: [1, 2], 1: [3], 2: [3], 3: []}
        self.nodes = [0, 1, 2, 3]

    def test_adjacency_matrix_to_dict(self):
        # Example: Node 0 connects to 1 and 2
        matrix = [
            [0, 1, 1],
            [0, 0, 0],
            [0, 0, 0]
        ]
        expected = {0: [1, 2], 1: [], 2: []}
        self.assertEqual(adjacency_matrix_to_dict(matrix), expected)

    def test_adjacency_matrix_to_dict_weighted(self):
        # Node 0 connects to 1 (weight 5) and 2 (weight 10)
        matrix = [
            [0, 5, 10],
            [0, 0, 0],
            [0, 0, 0]
        ]
        expected = {0: [(1, 5), (2, 10)], 1: [], 2: []}
        self.assertEqual(adjacency_matrix_to_dict(matrix, weighted=True), expected)

    def test_edge_list_dict_undirected(self):
        edges = [(0, 1), (1, 2)]
        # Expected: 0 connects to 1, 1 connects to 0 and 2, 2 connects to 1
        expected = {0: [1], 1: [0, 2], 2: [1]}
        result = edge_list_dict(edges, undirected=True)
        # Sort values to ensure comparison works regardless of list order
        for node in result:
            result[node].sort()
        self.assertEqual(result, expected)

    def test_edge_list_dict_directed(self):
        edges = [(0, 1), (1, 2)]
        expected = {0: [1], 1: [2]}
        self.assertEqual(edge_list_dict(edges, undirected=False), expected)

    def test_edge_list_dict_weighted_undirected(self):
        # Weighted edges: (u, v, weight)
        edges = [(0, 1, 5), (1, 2, 10)]
        expected = {
            0: [(1, 5)],
            1: [(0, 5), (2, 10)],
            2: [(1, 10)]
        }
        result = edge_list_dict(edges, undirected=True)
        self.assertEqual(result, expected)

    def test_edge_list_dict_weighted_directed(self):
        # Weighted edges: (u, v, weight)
        edges = [(0, 1, 5), (1, 2, 10)]
        expected = {
            0: [(1, 5)],
            1: [(2, 10)]
        }
        result = edge_list_dict(edges, undirected=False)
        self.assertEqual(result, expected)

    def test_empty_graph_transforms(self):
        self.assertEqual(adjacency_matrix_to_dict([]), {})
        self.assertEqual(edge_list_dict([]), {})

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

    def test_top_sort_disconnected_components(self):
        """Tests that nodes with no dependencies are handled correctly."""
        graph = {0: [1], 1: [], 2: [3], 3: []}
        nodes = [0, 1, 2, 3]

        result = topological_sort(nodes, graph)

        self.assertEqual(len(result), 4)
        self.assertTrue(result.index(0) < result.index(1))
        self.assertTrue(result.index(2) < result.index(3))

    def test_top_sort_single_node(self):
        """Edge case: Single node graph."""
        graph = {0: []}
        result = topological_sort([0], graph)
        self.assertEqual(result, [0])


if __name__ == '__main__':
    unittest.main()