import heapq
from collections import deque
from typing import Any, Tuple, Callable, Iterable


def search(q: deque[Tuple[Any, int]] | Any,
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

        if is_terminal(node, search_space, *args, **kwargs):
            return node, steps

        for nghbr in get_neighbors(node, search_space, *args, **kwargs):
            push((nghbr, steps))
    return None, float('inf')


from typing import Any, Tuple, Callable, Iterable, Deque, Dict


def bidirectional_search(
        start: Any,
        goal: Any,
        search_space: Any,
        q_f: Deque[Tuple[Any, int]],
        pop_f: Callable[[], Tuple[Any, int]],
        push_f: Callable[[Any], None],
        q_b: Deque[Tuple[Any, int]],
        pop_b: Callable[[], Tuple[Any, int]],
        push_b: Callable[[Any], None],
        get_neighbors: Callable[[Any, Any, Any, Any], Iterable[Any]],
        get_state: Callable[[Any], Any] = lambda n: n,
        *args,
        **kwargs
) -> Tuple[Any | None, int | float | None]:
    """
    Polymorphic bidirectional search.
    """
    visited_f: Dict[Any, int] = {}  # {state: steps}
    visited_b: Dict[Any, int] = {}  # {state: steps}

    # Initialize frontiers
    push_f((start, 0))
    push_b((goal, 0))

    while q_f and q_b:
        # Forward Step
        if q_f:
            node_f, steps_f = pop_f()
            state_f = get_state(node_f)

            # Check for intersection BEFORE marking as visited
            # This is the "safe" way to detect a meeting point
            if state_f in visited_b:
                return node_f, steps_f + visited_b[state_f]

            if state_f not in visited_f:
                visited_f[state_f] = steps_f
                for nghbr in get_neighbors(node_f, search_space, *args, **kwargs):
                    push_f((nghbr, steps_f + 1))

        # Backward Step
        if q_b:
            node_b, steps_b = pop_b()
            state_b = get_state(node_b)

            # Check for intersection BEFORE marking as visited
            if state_b in visited_f:
                return node_b, steps_b + visited_f[state_b]

            if state_b not in visited_b:
                visited_b[state_b] = steps_b
                for nghbr in get_neighbors(node_b, search_space, *args, **kwargs):
                    push_b((nghbr, steps_b + 1))

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
    def push(item):
        neighbor, steps = item
        q.append((neighbor, steps + 1))

    return search(q, search_space, q.popleft, push, is_terminal,
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
    def push(item):
        neighbor, steps = item
        q.append((neighbor, steps + 1))

    return search(q, search_space, q.pop, push, is_terminal,
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
                  is_terminal, get_neighbors, get_state, *args, **kwargs)


def dijkstra(start, search_space, is_terminal, get_neighbors, *args, **kwargs):
    """Dijsktra algorithm to find the shortest path in a weighted graph."""
    return a_star(start, search_space, is_terminal, get_neighbors, lambda n, s: 0, *args, **kwargs)
