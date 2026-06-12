from collections import deque
from typing import Any, Tuple, Callable, Iterable, List


def _search(q: deque[Tuple[Any, int]],
        search_space: Any,
        pop: Callable[[], Tuple[Any, int]],
        is_terminal: Callable[[Any, Any, Any], bool],
        get_neighbors: Callable[[Any, Any, Any, Any], Iterable[Any]],
        *args,
        **kwargs) -> Tuple[Any | None, int | float | None]:
    visited = set()
    while q:
        node, steps = pop()
        for nghbr in get_neighbors(node, search_space, *args, **kwargs):
            if nghbr not in visited:
                if is_terminal(nghbr, search_space, *args, **kwargs):
                    return nghbr, steps + 1
                q.append((nghbr, steps + 1))
    return None, float('inf')


def bfs(start: Any,
        search_space: Any,
        is_terminal: Callable[[Any, Any, Any], bool],
        get_neighbors: Callable[[Any, Any, Any, Any], Iterable[Any]],
        *args,
        **kwargs) -> Tuple[Any | None, int | float | None]:
    q = deque([(start, 0)])
    return _search(q, search_space, q.popleft, is_terminal, get_neighbors, *args, **kwargs)


def dfs(start: Any,
        search_space: Any,
        is_terminal: Callable[[Any, Any, Any], bool],
        get_neighbors: Callable[[Any, Any, Any, Any], Iterable[Any]],
        *args,
        **kwargs) -> Tuple[Any | None, int | float | None]:
    q = deque([(start, 0)])
    return _search(q, search_space, q.pop, is_terminal, get_neighbors, *args, **kwargs)
