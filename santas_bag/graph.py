import heapq
from collections import deque, defaultdict
from typing import Iterable, Dict, Any, List, Tuple, Set

from santas_bag.search import search, bfs


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


def transpose_graph(graph: Dict[Any, List[Any]]) -> Dict[Any, List[Any]]:
    """
    Take a graph and reverse the edges

    :param graph: The graph represented as dictionary mapping node -> list of neighbors

    :return: Dictionary mapping node -> list of neighbors
    """
    transposed = defaultdict(list)
    # Ensure all nodes from original graph are in the new dict
    for node in graph:
        if node not in transposed:
            transposed[node] = []

    for u, neighbors in graph.items():
        for neighbor in neighbors:
            # Handle both weighted and unweighted
            if isinstance(neighbor, tuple):
                v, w = neighbor
                transposed[v].append((u, w))
            else:
                transposed[neighbor].append(u)
    return dict(transposed)


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

def get_components(graph: Dict[Any, List[Any]]) -> List[Set[Any]]:
    """
    :param graph: Adjacency list where graph[u] = [v, ...] (u -> v)

    :return: List of Sets of nodes where each set is a component
    """
    def is_terminal(node, graph_, *args, **kwargs):
        return False

    unvisited = set(graph.keys())
    for neighbors in graph.values():
        for n in neighbors:
            v = n[0] if isinstance(n, tuple) else n
            unvisited.add(v)

    def get_neighbors(node, graph_, *args, **kwargs):
        for n_ in graph_.get(node, []):
            v_ = n_[0] if isinstance(n_, tuple) else n_
            if v_ in unvisited:
                yield v_

    components = []
    while unvisited:
        start_node = unvisited.pop()
        component = {start_node}

        def on_visit(node, _, *args, **kwargs):
            if node in unvisited:
                unvisited.remove(node)
                component.add(node)
            return False

        bfs(start_node, graph, on_visit, get_neighbors)
        components.append(component)

    return components


def spanning_tree(graph: Dict[Any, List[Tuple[Any, int]]]) -> List[Tuple[Any, Any, int]]:
    """
    Computes the Minimum Spanning Tree using Prim's algorithm.

    :param graph: Dict mapping node -> list of (neighbor, weight)

    :return: List of edges (u, v, weight) forming the MST
    """
    if not graph:
        return []

    # Start from an arbitrary node
    start_node = next(iter(graph))
    visited = {start_node}

    # Priority queue stores (weight, u, v) - ordered by weight
    edges = [
        (weight, start_node, neighbor)
        for neighbor, weight in graph[start_node]
    ]
    heapq.heapify(edges)
    mst_edges = []
    while edges:
        weight, u, v = heapq.heappop(edges)
        if v not in visited:
            visited.add(v)
            mst_edges.append((u, v, weight))

            # Add all edges from the newly added node to the queue
            for next_neighbor, next_weight in graph.get(v, []):
                if next_neighbor not in visited:
                    heapq.heappush(edges, (next_weight, v, next_neighbor))

    return mst_edges
