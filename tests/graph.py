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
        self.assertEqual({}, adjacency_matrix_to_dict([]))
        self.assertEqual({}, edge_list_dict([]))

    def test_transpose_unweighted(self):
        # 0 -> 1 -> 2
        graph = {0: [1], 1: [2], 2: []}
        expected = {0: [], 1: [0], 2: [1]}
        self.assertEqual(expected, transpose_graph(graph))

    def test_transpose_weighted(self):
        # 0 --(5)--> 1 --(10)--> 2
        graph = {0: [(1, 5)], 1: [(2, 10)], 2: []}
        expected = {0: [], 1: [(0, 5)], 2: [(1, 10)]}
        self.assertEqual(expected, transpose_graph(graph))

    def test_transpose_complex(self):
        # A cycle: 0 -> 1, 1 -> 0
        graph = {0: [1], 1: [0]}
        expected = {0: [1], 1: [0]}
        self.assertEqual(expected, transpose_graph(graph))

    def test_transpose_disconnected(self):
        graph = {0: [1], 2: [3]}
        expected = {0: [], 1: [0], 2: [], 3: [2]}
        self.assertEqual(expected, transpose_graph(graph))

    def test_transpose_empty(self):
        self.assertEqual({}, transpose_graph({}))

    def test_basic_topological_sort(self):
        """Standard DAG test where order must be [0, 1, 2, 3] or [0, 2, 1, 3]."""
        result = topological_sort(self.nodes, self.graph)
        # Verify length
        self.assertEqual(4, len(result))

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

        self.assertEqual(4, len(result))
        self.assertTrue(result.index(0) < result.index(1))
        self.assertTrue(result.index(2) < result.index(3))

    def test_top_sort_single_node(self):
        """Edge case: Single node graph."""
        graph = {0: []}
        result = topological_sort([0], graph)
        self.assertEqual(result, [0])

    def test_get_components(self):
        # Two separate clusters: (0, 1) and (2, 3)
        graph = {0: [1], 1: [0], 2: [3], 3: [2]}
        actual = get_components(graph)
        expected = [{0, 1}, {2, 3}]

        # Sort for comparison since set order is arbitrary
        actual_sorted = sorted([sorted(list(c)) for c in actual])
        expected_sorted = sorted([sorted(list(c)) for c in expected])

        self.assertEqual(expected_sorted, actual_sorted)

    def test_prims_algorithm(self):
        # A triangle: 0-1 (1), 1-2 (2), 0-2 (3)
        graph = {
            0: [(1, 1), (2, 3)],
            1: [(0, 1), (2, 2)],
            2: [(0, 3), (1, 2)]
        }

        expected = [(0, 1, 1), (1, 2, 2)]
        actual = spanning_tree(graph)

        # Normalize edges: sort vertices within each tuple, then sort the list of edges
        actual_normalized = sorted([tuple(sorted((u, v))) + (w,) for u, v, w in actual])
        self.assertEqual(expected, actual_normalized)

    def test_prims_empty(self):
        expected = []
        actual = spanning_tree({})
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()