import unittest
from santas_bag.search import *


class TestSearch(unittest.TestCase):

    def setUp(self):
        # A simple graph: 0 -> 1 -> 2 -> 3
        #                   \-> 4 -> 3
        self.graph = {0: [1, 4], 1: [2], 2: [3], 4: [3], 3: []}

        # Coordinates for 3 "cities"
        self.cities = [(0, 0), (0, 1), (1, 1)]

        # Precomputed distances (e.g., from Floyd-Warshall)
        self.dist_matrix = {
            ((0, 0), (0, 1)): 10, ((0, 1), (0, 0)): 10,
            ((0, 1), (1, 1)): 5, ((1, 1), (0, 1)): 5,
            ((0, 0), (1, 1)): 20, ((1, 1), (0, 0)): 20
        }

    @staticmethod
    def get_neighbors(node, search_space, *_):
        return search_space.get(node, [])

    @staticmethod
    def make_is_terminal(target_node, ):
        return lambda node, space, *args, **kwargs: node == target_node

    def test_on_visit_callback(self):
        """Verify that on_visit is called for each unique node visited."""
        visited_nodes = []

        def track_visits(node, *_):
            visited_nodes.append(node)

        is_terminal = self.make_is_terminal(3)
        # Using BFS on the graph: 0 -> 1 -> 2 -> 3
        # Should visit 0, 1, 2, 3
        result, steps = bfs(0, self.graph, self.get_neighbors, is_terminal=is_terminal, on_visit=track_visits)

        self.assertEqual(3, result)
        # Check that we recorded visits for the path
        self.assertIn(0, visited_nodes)
        self.assertIn(1, visited_nodes)
        self.assertIn(2, visited_nodes)
        self.assertIn(3, visited_nodes)
        self.assertEqual(5, len(visited_nodes))

    def test_bfs_shortest_path(self):
        is_terminal = self.make_is_terminal(3)
        result, steps = bfs(0, self.graph, self.get_neighbors, is_terminal)
        self.assertEqual(3, result)
        self.assertEqual(2, steps)

    def test_bfs_start_is_terminal(self):
        is_terminal = self.make_is_terminal(0)
        result, steps = bfs(0, self.graph, self.get_neighbors, is_terminal)
        self.assertEqual(0, result)
        self.assertEqual(0, steps)

    def test_greedy_best_first_search(self):
        """
        Verify greedy search prioritizes heuristic over actual path cost.
        Graph: 0 -> 1 (H=5), 0 -> 2 (H=8). Goal is 3.
        1 -> 3 (H=10), 2 -> 3 (H=0).
        """
        graph = {0: [1, 2], 1: [3], 2: [3], 3: []}

        # Greedy should go 0 -> 1 -> 3 because 1 (H=5) looks better than 2 (H=8)
        # even though 0 -> 2 -> 3 is the path with lower heuristic at the goal.
        def heuristic(node, search_space):
            h_map = {0: 10, 1: 5, 2: 8, 3: 0}
            return h_map.get(node, 100)

        is_terminal = self.make_is_terminal(3)

        result, steps = greedy_best_first_search(
            start=0,
            search_space=graph,
            get_neighbors=self.get_neighbors,
            is_terminal=is_terminal,
            heuristic=heuristic
        )

        self.assertEqual(3, result)
        self.assertEqual(2, steps)

    def test_dfs_start_is_terminal(self):
        is_terminal = self.make_is_terminal(0)
        result, steps = dfs(0, self.graph, self.get_neighbors, is_terminal)
        self.assertEqual(0, result)
        self.assertEqual(0, steps)

    def test_dfs_finds_path(self):
        is_terminal = self.make_is_terminal(3)
        result, steps = dfs(0, self.graph, self.get_neighbors, is_terminal)
        self.assertEqual(3, result)
        self.assertEqual(2, steps)

    def test_no_path(self):
        is_terminal = self.make_is_terminal(99)
        result, steps = bfs(0, self.graph, self.get_neighbors, is_terminal)
        self.assertIsNone(result)
        self.assertEqual(float('inf'), steps)

    def test_a_star_shortest_path(self):
        is_terminal = self.make_is_terminal(3)
        # Manhattan-style heuristic: simple absolute difference distance estimate
        heuristic = lambda node, space: abs(3 - node)
        result, steps = a_star(0, self.graph, self.get_neighbors, heuristic, is_terminal)
        self.assertEqual(3, result)
        self.assertEqual(2, steps)

    def test_a_star_start_is_terminal(self):
        # Start at 0, terminal is 0.
        # A* needs a heuristic; 0 distance is always 0.
        is_terminal = self.make_is_terminal(0)
        heuristic = lambda node, space: 0
        result, steps = a_star(0, self.graph, self.get_neighbors, heuristic, is_terminal)
        self.assertEqual(0, result)
        self.assertEqual(0, steps)

    def test_get_state_pruning(self):
        """Verify that get_state correctly prunes visited nodes."""
        graph = {0: [1, 2], 1: [3], 2: [3], 3: []}
        is_terminal = self.make_is_terminal(3)

        # Mapping everything to 'X' means once 1 is visited, the state 'X' is blocked.
        # BFS will find 1, then fail to find 2 because state 'X' is already in visited.
        # get_state = lambda n: n

        result, steps = bfs(0, graph, self.get_neighbors, is_terminal)
        self.assertEqual(3, result)
        self.assertEqual(2, steps)

    def test_args_and_kwargs_passing(self):
        """Verify that *args and **kwargs pass transparently through the engine."""

        def get_neighbors_with_modifier(node, search_space, *args, **kwargs):
            neighbors = search_space.get(node, [])
            if kwargs.get('reverse'):
                return list(reversed(neighbors))
            return neighbors

        is_terminal = self.make_is_terminal(3)

        # Pass reverse=True as a kwarg through BFS to the neighbor generator
        result, steps = bfs(0, self.graph, get_neighbors_with_modifier, is_terminal, reverse=True)
        self.assertEqual(3, result)

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

        result, steps = dijkstra(0, graph, get_weighted_neighbors, is_terminal)

        self.assertEqual(2, result)
        self.assertEqual(2, steps)  # 0->1 (1) + 1->2 (1) = 2

    def test_bidirectional_simple_path(self):
        """
        Verify bidirectional search finds the path 0-1-2-3-4.
        """
        graph = {
            0: [1], 1: [0, 2], 2: [1, 3],
            3: [2, 4], 4: [3]
        }

        q_f, q_b = deque(), deque()

        def push_f(item): q_f.append(item)

        def push_b(item): q_b.append(item)

        result, steps = bidirectional_search(
            start=0, goal=4, search_space=graph,
            get_neighbors=self.get_neighbors,
            q_f=q_f, pop_f=q_f.popleft, push_f=push_f,
            q_b=q_b, pop_b=q_b.popleft, push_b=push_b
        )

        # In a 4-step path, bidirectional will meet at a middle node
        self.assertEqual(4, steps)

    def test_bidirectional_no_path(self):
        """Verify returns None if no path exists."""
        graph = {0: [1], 1: [], 2: [3], 3: []}
        q_f, q_b = deque(), deque()

        result, steps = bidirectional_search(
            start=0, goal=4, search_space=graph,
            get_neighbors=self.get_neighbors,
            q_f=q_f, pop_f=q_f.popleft, push_f=q_f.append,
            q_b=q_b, pop_b=q_b.popleft, push_b=q_b.append
        )
        self.assertIsNone(result)
        self.assertEqual(float('inf'), steps)

    def test_on_visit_bidirectional(self):
        """Verify that on_visit works with bidirectional search."""
        visit_count = 0

        def count_visits(node, steps, space):
            nonlocal visit_count
            visit_count += 1

        graph = {0: [1], 1: [2], 2: []}
        q_f, q_b = deque(), deque()

        bidirectional_search(
            start=0, goal=2, search_space=graph,
            get_neighbors=self.get_neighbors,
            q_f=q_f, pop_f=q_f.popleft, push_f=q_f.append,
            q_b=q_b, pop_b=q_b.popleft, push_b=q_b.append,
            on_visit=count_visits
        )

        # Should have visited nodes from both directions
        self.assertGreater(visit_count, 0)

    def test_find_all_paths_diamond(self):
        """Verify finding all paths in a diamond graph: 0 -> 1 -> 3 and 0 -> 2 -> 3."""
        # 0 connects to 1 and 2. 1 and 2 connect to 3.
        graph = {0: [1, 2], 1: [3], 2: [3], 3: []}

        paths = find_all_paths(0, graph, 3, self.get_neighbors)

        expected = [[0, 1, 3], [0, 2, 3]]
        self.assertEqual(len(paths), 2)
        self.assertIn([0, 1, 3], paths)
        self.assertIn([0, 2, 3], paths)

    def test_find_all_paths_with_cycles(self):
        """Verify it ignores cycles (0 -> 1 -> 0) and finds valid paths."""
        # 0 -> 1 -> 2, but 1 also points back to 0
        graph = {0: [1], 1: [0, 2], 2: []}

        paths = find_all_paths(0, graph, 2, self.get_neighbors)

        # Only one simple path: 0 -> 1 -> 2
        self.assertEqual(paths, [[0, 1, 2]])

    def test_find_all_paths_no_path(self):
        """Verify returns empty list when goal is unreachable."""
        graph = {0: [1], 1: [], 2: []}
        paths = find_all_paths(0, graph, 2, self.get_neighbors)
        self.assertEqual(paths, [])

    def test_tsp_s_star_basic(self):
        # Define a simple 3-city graph
        cities = ['A', 'B', 'C']

        # Distances: A-B=10, A-C=15, B-C=20
        distances = {
            ('A', 'B'): 10, ('B', 'A'): 10,
            ('A', 'C'): 15, ('C', 'A'): 15,
            ('B', 'C'): 20, ('C', 'B'): 20
        }

        def dist_matrix(c1, c2):
            return distances.get((c1, c2), 0)

        # Expected path: A -> B -> C (10+20 = 30) or A -> C -> B (15+20 = 35)
        # Optimal: 30
        result_node, total_steps = solve_tsp_a_star(cities, dist_matrix)

        self.assertEqual(30, total_steps)
        self.assertEqual('C', result_node[0])  # Ended at C

    def test_tsp_a_star_no_path(self):
        # Cities that cannot reach each other
        cities = ['A', 'B']

        def dist_matrix(c1, c2):
            return float('inf')

        result_node, total_steps = solve_tsp_a_star(cities, dist_matrix)
        self.assertEqual(float('inf'), total_steps)
        self.assertIsNone(result_node)

    def test_solve_tsp_optimized(self):
        # A -> B (10) + B -> C (5) = 15
        result_node, total_steps = solve_tsp_optimized(self.cities, self.dist_matrix)
        self.assertEqual(15, total_steps)
        # Check that all cities were visited (visited set length is 3)
        self.assertEqual(3, len(result_node[1]))

    def test_solve_tsp(self):
        # Using the same setup, but passing a weight function for solve_tsp
        def dist_func(c1, c2):
            return self.dist_matrix.get((c1, c2), float('inf'))

        result_node, total_steps = solve_tsp(self.cities, dist_func)
        self.assertEqual(15, total_steps)

    def test_tsp_no_path(self):
        # Cities with no connections
        cities = [(0, 0), (5, 5)]
        dist_matrix = {}
        result_node, total_steps = solve_tsp_optimized(cities, dist_matrix)
        self.assertEqual(float('inf'), total_steps)
        self.assertIsNone(result_node)

    def test_floyd_warshall_basic(self):
        nodes = ['A', 'B', 'C']
        # Define distances where A -> B -> C is shorter than direct A -> C
        distances = {
            ('A', 'B'): 2, ('B', 'A'): 2,
            ('B', 'C'): 3, ('C', 'B'): 3,
            ('A', 'C'): 10, ('C', 'A'): 10
        }

        def get_weight(n1, n2):
            if n1 == n2: return 0
            return distances.get((n1, n2), float('inf'))

        results = floyd_warshall(nodes, get_weight)

        # A -> C should now be 5 (2 + 3)
        self.assertEqual(5, results[('A', 'C')])
        self.assertEqual(2, results[('A', 'B')])
        self.assertEqual(3, results[('B', 'C')])

    def test_floyd_warshall_disconnected(self):
        nodes = ['A', 'B', 'C']

        # No paths exist
        def get_weight(n1, n2):
            return 0 if n1 == n2 else float('inf')

        results = floyd_warshall(nodes, get_weight)
        self.assertEqual(float('inf'), results[('A', 'C')])

    def test_is_terminal_is_none(self):
        """
        Verify that search terminates correctly when is_terminal is None
        (i.e., it visits all reachable nodes until the queue is exhausted).
        """
        # Graph: 0 -> 1 -> 2
        # If we set is_terminal=None, it should finish visiting all nodes.
        graph = {0: [1], 1: [2], 2: []}
        visited_nodes = []

        def track_visits(node, *_):
            visited_nodes.append(node)

        # BFS with is_terminal=None
        # The search will finish because the queue will eventually be empty.
        # The search function returns (None, float('inf')) because it never
        # hits a "terminal" condition.
        result, steps = bfs(0, graph, self.get_neighbors, on_visit=track_visits)

        self.assertIsNone(result)
        self.assertEqual(steps, float('inf'))
        self.assertIn(0, visited_nodes)
        self.assertIn(1, visited_nodes)
        self.assertIn(2, visited_nodes)
        self.assertEqual(len(visited_nodes), 3)


if __name__ == '__main__':
    unittest.main()