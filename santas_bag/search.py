import heapq
from collections import deque
from typing import Any, Tuple, Callable, Iterable, Optional


def search(
        q: Any,
        search_space: Any,
        pop: Callable[[], Tuple[Any, int]],
        push: Callable[[Any], None],
        is_terminal: Callable[[Any, Any, Any], bool],
        get_neighbors: Callable[[Any, Any, Any, Any], Iterable[Any]],
        get_state: Callable[[Any], Any] = lambda n: n,
        *args,
        **kwargs
) -> Tuple[Optional[Any], int | float]:
    """
    A polymorphic engine for state-space traversal.

    :param q: The frontier/queue data structure.
    :param search_space: The environment or graph to navigate.
    :param pop: Function to extract the next (node, steps) from the frontier.
    :param push: Function to insert (node, steps) into the frontier.
    :param is_terminal: Predicate to identify the goal state.
    :param get_neighbors: Generator for adjacent nodes.
    :param get_state: Function to map a node to a hashable state for pruning.
    :param args: Additional positional arguments for callbacks.
    :param kwargs: Additional keyword arguments for callbacks.
    :return: A tuple of (terminal_node, total_steps). Returns (None, inf) if no path exists.

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
) -> Tuple[Optional[Any], int | float]:
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
    :param get_state: Function to map a node to a hashable state.
    :param args: Additional positional arguments for callbacks.
    :param kwargs: Additional keyword arguments for callbacks.

    Returns:
        A tuple of (terminal_node, total_steps). Returns (None, inf) if no path exists.
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

            if state not in visited:
                visited[state] = steps
                for nghbr in get_neighbors(node, search_space, *args, **kwargs):
                    push((nghbr, steps + 1))

    return None, float('inf')


def bfs(
        start: Any,
        search_space: Any,
        is_terminal: Callable[[Any, Any, Any], bool],
        get_neighbors: Callable[[Any, Any, Any, Any], Iterable[Any]],
        get_state: Callable[[Any], Any] = lambda n: n,
        *args,
        **kwargs
) -> Tuple[Optional[Any], int | float]:
    """
    Performs a Breadth-First Search to find the shortest path in an unweighted graph.

    :param start: The starting node.
    :param search_space: The environment or graph to navigate.
    :param is_terminal: Predicate to identify the goal state.
    :param get_neighbors: Generator for adjacent nodes.
    :param get_state: Function to map a node to a hashable state.
    :param args: Additional positional arguments for callbacks.
    :param kwargs: Additional keyword arguments for callbacks.

    Returns:
        A tuple of (terminal_node, total_steps). Returns (None, inf) if no path exists.
    """
    if is_terminal(start, search_space, *args, **kwargs):
        return start, 0

    q = deque([(start, 0)])
    def push(item):
        neighbor, steps = item
        q.append((neighbor, steps + 1))

    return search(q, search_space, q.popleft, push, is_terminal,
                  get_neighbors, get_state, *args, **kwargs)


import heapq

def greedy_best_first_search(
    start: Any,
    search_space: Any,
    is_terminal: Callable[..., bool],
    get_neighbors: Callable[..., Iterable[Any]],
    heuristic: Callable[[Any, Any], int],
    get_state: Callable[[Any], Any] = lambda n: n,
    *args,
    **kwargs
) -> Tuple[Optional[Any], int | float]:
    """
    Performs a Greedy Best-First Search to find a path quickly.

    :param start: The starting node.
    :param search_space: The environment or graph to navigate.
    :param is_terminal: Predicate to identify the goal state.
    :param get_neighbors: Generator for adjacent nodes.
    :param heuristic: A function calculating the estimated cost to the goal.
    :param get_state: Function to map a node to a hashable state.
    :param args: Additional positional arguments for callbacks.
    :param kwargs: Additional keyword arguments for callbacks.

    Returns:
        A tuple of (terminal_node, total_steps). Returns (None, inf) if no path exists.
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
        is_terminal, get_neighbors, get_state, *args, **kwargs
    )


def dfs(
        start: Any,
        search_space: Any,
        is_terminal: Callable[[Any, Any, Any], bool],
        get_neighbors: Callable[[Any, Any, Any, Any], Iterable[Any]],
        get_state: Callable[[Any], Any] = lambda n: n,
        *args,
        **kwargs
) -> Tuple[Optional[Any], int | float]:
    """
    Performs an iterative Depth-First Search for pathfinding.

    :param start: The starting node.
    :param search_space: The environment or graph to navigate.
    :param is_terminal: Predicate to identify the goal state.
    :param get_neighbors: Generator for adjacent nodes.
    :param get_state: Function to map a node to a hashable state.
    :param args: Additional positional arguments for callbacks.
    :param kwargs: Additional keyword arguments for callbacks.

    Returns:
        A tuple of (terminal_node, total_steps). Returns (None, inf) if no path exists.
    """
    if is_terminal(start, search_space, *args, **kwargs):
        return start, 0

    q = deque([(start, 0)])
    def push(item):
        neighbor, steps = item
        q.append((neighbor, steps + 1))

    return search(q, search_space, q.pop, push, is_terminal,
                  get_neighbors, get_state, *args, **kwargs)


def a_star(
        start: Any,
        search_space: Any,
        is_terminal: Callable[..., bool],
        get_neighbors: Callable[..., Iterable[Any]],
        heuristic: Callable[[Any, Any], int],
        get_state: Callable[[Any], Any] = lambda n: n,
        *args,
        **kwargs
) -> Tuple[Optional[Any], int | float]:
    """
    Performs A* search to find the shortest path in a weighted graph.

    :param start: The starting node.
    :param search_space: The environment or graph to navigate.
    :param is_terminal: Predicate to identify the goal state.
    :param get_neighbors: Generator for adjacent nodes.
    :param heuristic: A function calculating the estimated cost from a node to the goal.
    :param get_state: Function to map a node to a hashable state.
    :param args: Additional positional arguments for callbacks.
    :param kwargs: Additional keyword arguments for callbacks.

    Returns:
        A tuple of (terminal_node, total_steps). Returns (None, inf) if no path exists.
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


def dijkstra(
        start: Any,
        search_space: Any,
        is_terminal: Callable[..., bool],
        get_neighbors: Callable[..., Iterable[Any]],
        *args,
        **kwargs
) -> Tuple[Optional[Any], int | float]:
    """
    Performs Dijkstra's algorithm to find the shortest path in a weighted graph.

    :param start: The starting node.
    :param search_space: The environment or graph to navigate.
    :param is_terminal: Predicate to identify the goal state.
    :param get_neighbors: Generator for adjacent nodes.
    :param args: Additional positional arguments for callbacks.
    :param kwargs: Additional keyword arguments for callbacks.

    Returns:
        A tuple of (terminal_node, total_steps). Returns (None, inf) if no path exists.
    """
    return a_star(start, search_space, is_terminal, get_neighbors, lambda n, s: 0, *args, **kwargs)
