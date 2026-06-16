import heapq
from collections import deque
from typing import Any, Tuple, Callable, Iterable, List, Dict


def _search(q: deque[Tuple[Any, int]] | Any,
            search_space: Any,
            pop: Callable[[], Tuple[Any, int]],
            push: Callable[[Any], None],
            is_terminal: Callable[[Any, Any, Any], bool],
            get_neighbors: Callable[[Any, Any, Any, Any], Iterable[Any]],
            get_state: Callable[[Any], Any] = lambda n: n,
            *args,
            **kwargs) -> Tuple[Any | None, int | float | None]:
    """
        A polymorphic engine for state-space traversal.

        Args:
            q: A queue-like object used to hold nodes to be explored.
            search_space: The environment, map, or rulebook to navigate.
            pop: A function to extract a (node, steps) tuple from q.
            push: A function to add a (node, steps) tuple to q.
            is_terminal: A predicate to identify the goal state.
            get_neighbors: A generator function returning adjacent nodes.
            get_state: An optional function to transform a node into its hashable
                       state representation for cycle detection.
            *args, **kwargs: Contextual data passed through to callbacks.

        Returns:
            A tuple of (terminal_node, total_steps). Returns (None, inf) if no path exists.
        """
    visited = set()
    while q:
        node, steps = pop()
        state = get_state(node)
        if state in visited:
            continue
        visited.add(state)

        for nghbr in get_neighbors(node, search_space, *args, **kwargs):
            if is_terminal(nghbr, search_space, *args, **kwargs):
                return nghbr, steps + 1
            push((nghbr, steps + 1))
    return None, float('inf')


def bfs(start: Any,
        search_space: Any,
        is_terminal: Callable[[Any, Any, Any], bool],
        get_neighbors: Callable[[Any, Any, Any, Any], Iterable[Any]],
        get_state: Callable[[Any], Any] = lambda n: n,
        *args,
        **kwargs) -> Tuple[Any | None, int | float | None]:
    """Performs a Breadth-First Search to find the shortest path in an unweighted graph."""
    if is_terminal(start, search_space, *args, **kwargs):
        return start, 0

    q = deque([(start, 0)])
    return _search(q, search_space, q.popleft, q.append, is_terminal,
                   get_neighbors, get_state, *args, **kwargs)


def dfs(start: Any,
        search_space: Any,
        is_terminal: Callable[[Any, Any, Any], bool],
        get_neighbors: Callable[[Any, Any, Any, Any], Iterable[Any]],
        get_state: Callable[[Any], Any] = lambda n: n,
        *args,
        **kwargs) -> Tuple[Any | None, int | float | None]:
    """Performs an iterative Depth-First Search for pathfinding."""
    if is_terminal(start, search_space, *args, **kwargs):
        return start, 0

    q = deque([(start, 0)])
    return _search(q, search_space, q.pop, q.append, is_terminal,
                   get_neighbors, get_state, *args, **kwargs)


def a_star(start: Any,
           search_space: Any,
           is_terminal: Callable[..., bool],
           get_neighbors: Callable[..., Iterable[Any]],
           heuristic: Callable[[Any, Any], int],
           get_state: Callable[[Any], Any] = lambda n: n,
           *args,
           **kwargs) -> Tuple[Any | None, int | float | None]:
    """
        Performs A* search to find the shortest path in a weighted graph.

        :param heuristic: a function calculating the estimated cost from a node to the goal.
        """
    if is_terminal(start, search_space, *args, **kwargs):
        return start, 0

    q = [(heuristic(start, search_space), 0, start)]
    heapq.heapify(q)

    def priority_pop():
        f, steps, node = heapq.heappop(q)
        return node, steps

    def priority_append(item):
        node, steps = item
        f = steps + heuristic(node, search_space)
        heapq.heappush(q, (f, steps, node))

    return _search(q, search_space, priority_pop, priority_append,
                   is_terminal, get_neighbors, get_state, *args, **kwargs)


def topological_sort(nodes: Iterable[Any],
                     graph: Dict[Any, List[Any]],
                     in_degrees: Dict[Any, int]):
    """
    Kahn's Algorithm implementation using the search engine.
    :param nodes: the nodes in the graph.
    :param graph: Adjacency list where graph[u] = [v, ...] (u -> v)
    :param in_degrees: dict tracking how many dependencies each node has
    """
    initial_nodes = [n for n in nodes if in_degrees.get(n, 0) == 0]
    q = deque([(n, 0) for n in initial_nodes])
    sorted_order = initial_nodes[:]

    def push(item):
        node, _ = item
        sorted_order.append(node)
        q.append(item)

    def get_neighbors(node, graph_, *args, **kwargs):
        for neighbor in graph_.get(node, []):
            in_degrees[neighbor] -= 1
            if in_degrees[neighbor] == 0:
                yield neighbor

    _search(q, graph, q.popleft, push, lambda *args: False, get_neighbors)

    return sorted_order


