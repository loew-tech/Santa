from collections import deque, defaultdict
from typing import Iterable, Dict, Any, List, Tuple

from santas_bag.search import search


def adjacency_matrix_to_dict(
        adjacency_lists: List[List],
        weighted=False
) -> Dict[int, List[int]]:
    """
    Transform a list of adjacency matrix into a graph dictionary mapping node -> neighbors.
    :param weighted: Bool flag if graph is weighted or not. Default is False
    :param adjacency_lists: List of adjacency

    :return: Dictionary mapping node -> list of neighbors
    """
    graph = {}
    for y, adjacency_list in enumerate(adjacency_lists):
        neighbors = []
        for x, val in enumerate(adjacency_list):
            if val:
                neighbors.append(x if not weighted else (x, val))
        graph[y] = neighbors
    return graph


def edge_list_dict(edge_list: List[Tuple], undirected=True) -> Dict[Any, List[Any]]:
    """
    Transform a list of edges into a graph dictionary mapping node -> neighbors.
    Supports unweighted graphs and weighted graphs in form (vertex1, vertex2, weight).

    :param edge_list: List of tuples of (node1, node2) where nodes are connected
    :param undirected: Bool for if graph is undirected or not. Default is True

    :return: Dictionary mapping node -> list of neighbors
    """
    graph = defaultdict(list)
    for u, v, *wght in edge_list:
        if wght:
            w = wght[0]
            graph[u].append((v, w))
            if undirected:
                graph[v].append((u, w))
            continue

        graph[u].append(v)
        if undirected:
            graph[v].append(u)
    return graph


def topological_sort(nodes: Iterable[Any],
                     graph: Dict[Any, List[Any]]) -> List[Any]:
    """
    Kahn's Algorithm implementation using the search engine.

    :param nodes: The nodes in the graph.
    :param graph: Adjacency list where graph[u] = [v, ...] (u -> v)

    :return: List of nodes in topological order
    """
    in_degrees = {n: 0 for n in nodes}
    for u in graph:
        for v in graph[u]:
            in_degrees[v] = in_degrees.get(v, 0) + 1

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

    search(q, graph, q.popleft, push, lambda *args: False, get_neighbors)

    return sorted_order