import heapq
from collections import deque
from typing import Any, Tuple, Callable, Iterable, List


def _search(q: deque[Tuple[Any, int]] | Any,
        search_space: Any,
        pop: Callable[[], Tuple[Any, int]],
        append: Callable[[Any], None],
        is_terminal: Callable[[Any, Any, Any], bool],
        get_neighbors: Callable[[Any, Any, Any, Any], Iterable[Any]],
        get_state: Callable[[Any], Any] = lambda n: n,
        *args,
        **kwargs) -> Tuple[Any | None, int | float | None]:
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
            append((nghbr, steps + 1))
    return None, float('inf')


def bfs(start: Any,
        search_space: Any,
        is_terminal: Callable[[Any, Any, Any], bool],
        get_neighbors: Callable[[Any, Any, Any, Any], Iterable[Any]],
        *args,
        **kwargs) -> Tuple[Any | None, int | float | None]:
    q = deque([(start, 0)])
    return _search(q, search_space, q.popleft, q.append,
                   is_terminal, get_neighbors, *args, **kwargs)


def dfs(start: Any,
        search_space: Any,
        is_terminal: Callable[[Any, Any, Any], bool],
        get_neighbors: Callable[[Any, Any, Any, Any], Iterable[Any]],
        *args,
        **kwargs) -> Tuple[Any | None, int | float | None]:
    q = deque([(start, 0)])
    return _search(q, search_space, q.pop, q.append, is_terminal,
                   get_neighbors, *args, **kwargs)


def a_star(start: Any,
           search_space: Any,
           is_terminal: Callable[..., bool],
           get_neighbors: Callable[..., Iterable[Any]],
           heuristic: Callable[[Any, Any], int],
           *args,
           **kwargs) -> Tuple[Any | None, int | float | None]:
    q_data = [(heuristic(start, search_space), 0, start)]
    heapq.heapify(q_data)

    def priority_pop():
        f, steps, node = heapq.heappop(q_data)
        return node, steps

    def priority_append(item):
        node, steps = item
        f = steps + heuristic(node, search_space)
        heapq.heappush(q_data, (f, steps, node))

    return _search(q_data, search_space, priority_pop, priority_append,
                   is_terminal, get_neighbors, *args, **kwargs)

