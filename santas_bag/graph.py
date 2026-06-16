from collections import deque
from typing import Iterable, Dict, Any, List

from santas_bag.search import _search


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