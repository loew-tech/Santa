import heapq
from collections import deque
from typing import Any, Tuple, Callable, Iterable, Deque, Dict, Optional, List

from santas_bag.types import Node, NeighborFunction


def search(
        q: Iterable[Node],
        search_space: Any,
        pop: Callable[[], Tuple[Node, int]],
        push: Callable[[Tuple[Node, int]], None],
        is_terminal: Callable[[Node, Any, Any], bool],
        get_neighbors: NeighborFunction,
        on_visit: Optional[Callable[[Node, int, Any], None]] = None,
        get_state: Callable[[Node], Any] = lambda n: n,
        revisit=False,
        *args,
        **kwargs
) -> Tuple[Optional[Node], int | float]:
    """
    A polymorphic engine for state-space traversal.

    :param q: The frontier/queue data structure.
    :param search_space: The environment or graph to navigate.
    :param pop: Function to extract the next (node, steps) from the frontier.
    :param push: Function to insert (node, steps) into the frontier.
    :param is_terminal: Predicate to identify the goal state.
    :param get_neighbors: Generator for adjacent nodes.
    :param on_visit: Function taking (node, steps, search_space) to call on visited state.
    :param get_state: Function to map a node to a hashable state for pruning.
    :param revisit: Flag indicating if nodes should be revisited.
    :param args: Additional positional arguments for callbacks.
    :param kwargs: Additional keyword arguments for callbacks.

    :return: A tuple of (terminal_node, total_steps). Returns (None, inf) if no path exists.
    """
    visited = set()
    while q:
        node, steps = pop()
        state = get_state(node)
        if not revisit and state in visited:
            continue
        visited.add(state)

        if on_visit is not None:
            on_visit(node, steps, search_space)

        if is_terminal(node, search_space, *args, **kwargs):
            return node, steps

        for nghbr in get_neighbors(node, search_space, *args, **kwargs):
            push((nghbr, steps))

    return None, float('inf')


def bidirectional_search(
        start: Node,
        goal: Node,
        search_space: Any,
        q_f: Deque[Tuple[Node, int]],
        pop_f: Callable[[], Tuple[Node, int]],
        push_f: Callable[[Node], None],
        q_b: Deque[Tuple[Node, int]],
        pop_b: Callable[[], Tuple[Node, int]],
        push_b: Callable[[Node], None],
        get_neighbors: NeighborFunction[Node],
        on_visit: Optional[Callable[[Node, int, Any], None]] = None,
        get_state: Callable[[Node], Any] = lambda n: n,
        revisit=False,
        *args,
        **kwargs
) -> Tuple[Optional[Node], int | float]:
    """
    Performs a polymorphic bidirectional search to find the shortest path between start and goal.

    :param start: The starting node.
    :param goal: The target node.
    :param search_space: The environment or graph to navigate.
    :param q_f: The forward frontier queue.
    :param pop_f: Function to extract from forward frontier.
    :param push_f: Function to insert into forward frontier.
    :param q_b: The backward frontier queue.
    :param pop_b: Function to extract from backward frontier.
    :param push_b: Function to insert into backward frontier.
    :param get_neighbors: Generator for adjacent nodes.
    :param on_visit: Function taking (node, steps, search_space) to call on visited state. Note steps is steps from start
    :param get_state: Function to map a node to a hashable state.
    :param revisit: Flag indicating if nodes should be revisited.
    :param args: Additional positional arguments for callbacks.
    :param kwargs: Additional keyword arguments for callbacks.

    :return a tuple of (terminal_node, total_steps). Returns (None, inf) if no path exists.
    """
    visited_f: Dict[Any, int] = {}  # {state: steps}
    visited_b: Dict[Any, int] = {}  # {state: steps}

    # Initialize frontiers
    push_f((start, 0))
    push_b((goal, 0))

    search_elements = (
        (q_f, pop_f, push_f, visited_f, visited_b),
        (q_b, pop_b, push_b, visited_b, visited_f)
    )

    while q_f and q_b:
        for q, pop, push, visited, other_visited in search_elements:
            node, steps = pop()
            state = get_state(node)
            if state in other_visited:
                return node, steps + other_visited[state]

            if on_visit is not None:
                on_visit(node, steps, search_space)

            if revisit or state not in visited:
                visited[state] = steps
                for nghbr in get_neighbors(node, search_space, *args, **kwargs):
                    push((nghbr, steps + 1))

    return None, float('inf')


def bfs(
        start: Node,
        search_space: Any,
        is_terminal: Callable[[Node, Any, Any], bool],
        get_neighbors: NeighborFunction[Node],
        on_visit: Optional[Callable[[Node, int, Any], None]] = None,
        get_state: Callable[[Node], Any] = lambda n: n,
        revisit=False,
        *args,
        **kwargs
) -> Tuple[Optional[Node], int | float]:
    """
    Performs a Breadth-First Search to find the shortest path in an unweighted graph.

    :param start: The starting node.
    :param search_space: The environment or graph to navigate.
    :param is_terminal: Predicate to identify the goal state.
    :param get_neighbors: Generator for adjacent nodes.
    :param on_visit: Function taking (node, steps, search_space) to call on visited state.
    :param get_state: Function to map a node to a hashable state.
    :param revisit: Flag indicating if nodes should be revisited.
    :param args: Additional positional arguments for callbacks.
    :param kwargs: Additional keyword arguments for callbacks.

    :return a tuple of (terminal_node, total_steps). Returns (None, inf) if no path exists.
    """
    if is_terminal(start, search_space, *args, **kwargs):
        return start, 0

    q = deque([(start, 0)])
    def push(item):
        neighbor, steps = item
        q.append((neighbor, steps + 1))

    return search(q, search_space, q.popleft, push, is_terminal,
                  get_neighbors, on_visit, get_state, revisit, *args, **kwargs)


def greedy_best_first_search(
    start: Node,
    search_space: Any,
    is_terminal: Callable[..., bool],
    get_neighbors: NeighborFunction[Node],
    heuristic: Callable[[Node, Any], int],
    on_visit: Optional[Callable[[Node, int, Any], None]] = None,
    get_state: Callable[[Node], Any] = lambda n: n,
    revisit=False,
    *args,
    **kwargs
) -> Tuple[Optional[Node], int | float]:
    """
    Performs a Greedy Best-First Search to find a path quickly.

    :param start: The starting node.
    :param search_space: The environment or graph to navigate.
    :param is_terminal: Predicate to identify the goal state.
    :param get_neighbors: Generator for adjacent nodes.
    :param heuristic: A function calculating the estimated cost to the goal.
    :param on_visit: Function taking (node, steps, search_space) to call on visited state.
    :param get_state: Function to map a node to a hashable state.
    :param revisit: Flag indicating if nodes should be revisited.
    :param args: Additional positional arguments for callbacks.
    :param kwargs: Additional keyword arguments for callbacks.

    :return a tuple of (terminal_node, total_steps). Returns (None, inf) if no path exists.
    """
    q = [(heuristic(start, search_space), start, 0)]
    heapq.heapify(q)

    def priority_pop():
        h, node, steps = heapq.heappop(q)
        return node, steps

    def priority_push(item):
        neighbor, steps = item
        priority = heuristic(neighbor, search_space)
        heapq.heappush(q, (priority, neighbor, steps + 1))

    return search(
        q, search_space, priority_pop, priority_push,
        is_terminal, get_neighbors, on_visit, get_state, revisit, *args, **kwargs
    )


def dfs(
        start: Node,
        search_space: Any,
        is_terminal: Callable[[Node, Any, Any], bool],
        get_neighbors: NeighborFunction[Node],
        on_visit: Optional[Callable[[Node, int, Any], None]] = None,
        get_state: Callable[[Node], Any] = lambda n: n,
        revisit=False,
        *args,
        **kwargs
) -> Tuple[Optional[Node], int | float]:
    """
    Performs an iterative Depth-First Search for pathfinding.

    :param start: The starting node.
    :param search_space: The environment or graph to navigate.
    :param is_terminal: Predicate to identify the goal state.
    :param get_neighbors: Generator for adjacent nodes.
    :param on_visit: Function taking (node, steps, search_space) to call on visited state.
    :param get_state: Function to map a node to a hashable state.
    :param revisit: Flag indicating if nodes should be revisited.
    :param args: Additional positional arguments for callbacks.
    :param kwargs: Additional keyword arguments for callbacks.

    :return a tuple of (terminal_node, total_steps). Returns (None, inf) if no path exists.
    """
    q = deque([(start, 0)])
    def push(item):
        neighbor, steps = item
        q.append((neighbor, steps + 1))

    return search(q, search_space, q.pop, push, is_terminal,
                  get_neighbors, on_visit, get_state, revisit,*args, **kwargs)


def find_all_paths(
        start: Node,
        search_space: Any,
        goal: Node,
        get_neighbors: NeighborFunction[Node],
        get_state: Callable[[Node], Any] = lambda n: n[0] if isinstance(n, tuple) else n,
        *args,
        **kwargs
) -> List[List]:
    """
    Finds all paths from start to goal.

    :param start: The starting node.
    :param search_space: The environment or graph to navigate.
    :param goal: Terminal node to reach.
    :param get_neighbors: Generator for adjacent nodes.
    :param get_state: Function to map a node to a hashable state.
    :param args: Additional positional arguments for callbacks.
    :param kwargs: Additional keyword arguments for callbacks.

    :return a tuple of (terminal_node, total_steps). Returns (None, inf) if no path exists.
    """
    all_paths = []
    def on_visit(node, *_):
        nd, path = node
        if nd == goal:
            all_paths.append(path)

    def is_terminal(*_):
        return False

    def neighbors(node, space, *args_, **kwargs_):
        nd, path = node
        if nd == goal:
            return []

        ret = []
        for nghbr in get_neighbors(nd, space, *args_, **kwargs_):
            if nghbr not in path:
                ret.append((nghbr, path + [nghbr]))
        return ret

    q = deque([((start, [start]), 0)])
    search(q, search_space, q.pop, q.append, is_terminal,
                  neighbors, on_visit, get_state, revisit=True,*args, **kwargs)
    return all_paths


def a_star(
        start: Node,
        search_space: Any,
        is_terminal: Callable[..., bool],
        get_neighbors: NeighborFunction[Node],
        heuristic: Callable[[Node, Any], int | float | Any],
        on_visit: Optional[Callable[[Node, int, Any], None]] = None,
        get_state: Callable[[Node], Any] = lambda n: n,
        *args,
        **kwargs
) -> Tuple[Optional[Node], int | float]:
    """
    Performs A* search to find the shortest path in a weighted graph.

    :param start: The starting node.
    :param search_space: The environment or graph to navigate.
    :param is_terminal: Predicate to identify the goal state.
    :param get_neighbors: Generator for adjacent nodes.
    :param heuristic: A function calculating the estimated cost from a node to the goal.
    :param on_visit: Function taking (node, steps, search_space) to call on visited state.
    :param get_state: Function to map a node to a hashable state.
    :param args: Additional positional arguments for callbacks.
    :param kwargs: Additional keyword arguments for callbacks.

    :return a tuple of (terminal_node, total_steps). Returns (None, inf) if no path exists.
    """
    if is_terminal(start, search_space, *args, **kwargs):
        return start, 0

    q = [(heuristic(start, search_space), 0, start)]
    heapq.heapify(q)

    def priority_pop():
        f, steps, node = heapq.heappop(q)
        return node, steps

    def priority_push(item):
        neighbor_info, current_steps = item

        # Robust unpacking: handle raw node OR (node, weight) tuple
        if isinstance(neighbor_info, tuple) and len(neighbor_info) == 2:
            neighbor, weight = neighbor_info
        else:
            neighbor, weight = neighbor_info, 1

        new_total_steps = current_steps + weight
        f = new_total_steps + heuristic(neighbor, search_space)
        heapq.heappush(q, (f, new_total_steps, neighbor))

    return search(q, search_space, priority_pop, priority_push,
                  is_terminal, get_neighbors, on_visit, get_state, *args, **kwargs)


def dijkstra(
        start: Node,
        search_space: Any,
        is_terminal: Callable[..., bool],
        get_neighbors: NeighborFunction[Node],
        on_visit: Optional[Callable[[Node, int, Any], None]] = None,
        *args,
        **kwargs
) -> Tuple[Optional[Node], int | float]:
    """
    Performs Dijkstra's algorithm to find the shortest path in a weighted graph.

    :param start: The starting node.
    :param search_space: The environment or graph to navigate.
    :param is_terminal: Predicate to identify the goal state.
    :param get_neighbors: Generator for adjacent nodes.
    :param on_visit: Function taking (node, steps, search_space) to call on visited state.
    :param args: Additional positional arguments for callbacks.
    :param kwargs: Additional keyword arguments for callbacks.

    :return a tuple of (terminal_node, total_steps). Returns (None, inf) if no path exists.
    """
    return a_star(start,
                  search_space,
                  is_terminal,
                  get_neighbors,
                  lambda n, s: 0,
                  on_visit,
                  *args,
                  **kwargs)

def solve_tsp_a_star(destinations: List[Node],
                     distance_func: Callable[[Node, Any], int | float | Any],
                     on_visit: Optional[Callable[[Node, int, Any], None]] = None) -> Tuple[Optional[Node], int | float]:
    """
    Solves TSP using A*.
    State = (current_destination, frozenset(visited_destination))

    :param destinations: List of destinations to visit.
    :param distance_func: Function to calculate the distance between two destinations.
    :param on_visit: Function taking (node, steps, search_space) to call on visited state.

    :return: A tuple of (terminal_node, total_steps). Returns (None, inf) if no path
    """
    start_destination = destinations[0]

    # 1. Terminal condition: Visited all destinations and returned to start (or just visited all)
    def is_terminal(state_node, _):
        current_destination, visited = state_node
        return len(visited) == len(destinations)

    # 2. Neighbors: Move to any unvisited destination
    def get_neighbors(state_node, *_):
        current_destination, visited = state_node
        for next_destination in destinations:
            if next_destination not in visited:
                weight = distance_func(current_destination, next_destination)
                # Only yield if a valid path exists
                if weight != float('inf'):
                    yield (next_destination, visited | {next_destination}), weight

    # 3. Heuristic: A simple MST or Minimum Outgoing Edge heuristic
    # (Here we use 0, making it effectively Dijkstra's, but you can improve this)
    def heuristic(state_node, _):
        current_destination, visited = state_node
        unvisited = [d for d in destinations if d not in visited]
        if not unvisited:
            return 0
        # Estimate: the shortest distance to any unvisited destination
        return min(distance_func(current_destination, c) for c in unvisited)

    # 4. State mapping: Used for the 'visited' set to prune cycles
    def get_state(state_node):
        return state_node  # (current, frozenset_visited) is already hashable

    # Initial state
    start_state = (start_destination, frozenset([start_destination]))

    return a_star(
        start_state,
        None,
        is_terminal,
        get_neighbors,
        heuristic,
        on_visit,
        get_state
    )


def solve_tsp_optimized(destinations: List[Tuple[int, int]],
                        distance_matrix: Dict[Tuple[Tuple[int, int], Tuple[int, int]], int | float | Any],
                        on_visit: Optional[Callable[[Node, int, Any], None]] = None) -> Tuple[Optional[Node], int | float]:
    """
    Solves TSP using A* to find the shortest path in a weighted graph.

    :param destinations: List of destinations to visit.
    :param distance_matrix: Dictionary mapping (start, end) to distance.
    :param on_visit: Function taking (node, steps, search_space) to call on visited state.

    :return A tuple of (terminal_node, total_steps). Returns (None, inf) if no path
    """
    def dist_func(c1, c2):
        return distance_matrix.get((c1, c2), float('inf'))
    return solve_tsp_a_star(destinations, dist_func, on_visit)


def solve_tsp(destinations: List[Any],
              distance_func: Callable[[Any, Any], int | float | Any],
              on_visit: Optional[Callable[[Any, int, Any], None]] = None) -> Tuple[Optional[Any], int | float]:
    """
    Solves TSP using floyd-warshall algorithm to find dictionary (start, stop): shortest_distance and then use
    that dictionary as distance_matrix for solve_tsp_optimized.

    :param destinations: list of destinations to visit.
    :param distance_func:
    :param on_visit: Function taking (node, steps, search_space) to call on visited state.

    :return: A tuple of (terminal_node, total_steps). Returns (None, inf) if no path
    """
    distances = floyd_warshall(destinations, distance_func)
    return solve_tsp_optimized(destinations, distances, on_visit)


def floyd_warshall(nodes: List[Any],
                   get_weight: Callable[[Any, Any], int | float]) -> Dict[Tuple[Any, Any], int | float | Any]:
    """
    Computes all-pairs shortest paths using the Floyd-Warshall algorithm.

    :param nodes: A list of all nodes in the graph.
    :param get_weight: A function returning the direct weight between two nodes.

    :return: A dictionary mapping (start, end) of shortest path distance.
    """
    dist = {(i, j): get_weight(i, j) for i in nodes for j in nodes}
    for k in nodes:
        for i in nodes:
            for j in nodes:
                if dist[(i, k)] + dist[(k, j)] < dist[(i, j)]:
                    dist[(i, j)] = dist[(i, k)] + dist[(k, j)]
    return dist
