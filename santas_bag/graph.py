import heapq
from collections import deque, defaultdict
from typing import Iterable, Dict, List, Set, Callable, Tuple, Any

from santas_bag.search import search, bfs, dfs


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


def adjacency_lists_to_dict(
        adjacency_list: List[Tuple[str, List[Any]]],
        undirected: bool = False
) -> Dict[str, List[Any]]:
    """
    Converts a parsed adjacency list into a graph dictionary.

    :param adjacency_list: List of (vertex, [neighbors]).
                           Neighbors can be simple values or (neighbor, weight) tuples.
    :param undirected: If True, adds reverse edges for all connections.
    """
    # Initialize the graph with primary edges
    graph = {vertex: list(edges) for vertex, edges in adjacency_list}

    # Ensure all mentioned neighbors exist as keys in the graph
    for vertex, edges in adjacency_list:
        for edge in edges:
            neighbor = edge[0] if isinstance(edge, tuple) else edge
            if neighbor not in graph:
                graph[neighbor] = []

            # If undirected, add the reverse connection
            if undirected:
                # Determine weight if it exists
                weight = edge[1] if isinstance(edge, tuple) else None

                # Create the reverse entry
                reverse_entry = (vertex, weight) if weight is not None else vertex

                # Avoid adding duplicates if the edge is already defined
                if reverse_entry not in graph[neighbor]:
                    graph[neighbor].append(reverse_entry)

    return graph


def edge_list_to_dict(edge_list: List[Tuple], undirected=True) -> Dict[Any, List[Any]]:
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


# @TODO: change this to graph: Dict[Node, Iterable[Node]]
def transpose_graph(graph: Dict[Any, List[Any]]) -> Dict[Any, List[Any]]:
    """
    Take a graph and reverse the edges

    :param graph: Adjacency list where graph[u] = [v, ...] (u -> v)

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


def graph_bfs(graph: Dict[Any, List[Any]],
              start: Any,
              goal: Any,
              get_neighbors: Callable[..., Iterable] | None = None) -> tuple[Any | None, int | float]:
    """
    Performs a BFS on the graph from start searching for goal.
    Returns the node for goal and the distance to get there

    :param graph: Adjacency list where graph[u] = [v, ...] (u -> v)
    :param start: Node to start from
    :param goal: node ID to find
    :param get_neighbors: Optional function for getting neighbors, default to graph[node]

    :return: A tuple of node for goal and distance to get there
    """
    if get_neighbors is None:
        get_neighbors = _get_neighbors_default

    return bfs(start, graph, _get_is_terminal_default(goal), get_neighbors)


def graph_dfs(graph: Dict[Any, List[Any]],
              start: Any,
              goal: Any,
              get_neighbors: Callable[..., Iterable] | None = None) -> tuple[Any | None, int | float]:
    """
    Performs a DFS on the graph from start searching for goal.
    Returns the node for goal and the distance to get there

    :param graph: Adjacency list where graph[u] = [v, ...] (u -> v)
    :param start: Node to start from
    :param goal: node ID to find
    :param get_neighbors: Optional function for getting neighbors, default to graph[node]

    :return: A tuple of node for goal and distance to get there
    """

    if get_neighbors is None:
        get_neighbors = _get_neighbors_default

    return dfs(start,
               graph,
               _get_is_terminal_default(goal),
               get_neighbors)


def get_in_degrees(graph: Dict[Any, List[Any]],
              nodes: Iterable[Any]) -> Dict[Any, int]:
    """
    Returns a dictionary mapping node id to in degree

    :param graph: Adjacency list where graph[u] = [v, ...] (u -> v)
    :param nodes: Node ids in the graph

    :return: Dict node -> in degree
    """
    in_degrees = {n: 0 for n in nodes}
    for u in graph:
        for v in graph[u]:
            if isinstance(v, tuple):
                v = v[0]
            in_degrees[v] = in_degrees.get(v, 0) + 1
    return in_degrees


def topological_sort(graph: Dict[Any, List[Any]],
                     nodes: Iterable[Any]) -> List[Any]:
    """
    Kahn's Algorithm implementation using the search engine.

    :param graph: Adjacency list where graph[u] = [v, ...] (u -> v)
    :param nodes: The nodes in the graph.

    :return: List of nodes in topological order
    """
    in_degrees = get_in_degrees(graph, nodes)

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


def get_component_for_node(graph: Dict[Any, List],
                           start_node: Any,
                           get_neighbors: Callable[..., Iterable] | None = None) -> Set[Any]:
    """
    Returns the set of all nodes reachable from the start_node.

    :param graph: The graph dictionary.
    :param start_node: The node to begin the search from.
    :param get_neighbors: A callback for getting the neighbors of the current node

    :return: A set of nodes comprising the connected component.
    """
    if start_node not in graph:
        return set()

    if get_neighbors is None:
        get_neighbors = _get_neighbors_default

    visited = set()
    bfs(start_node,
        graph,
        lambda n, s, *args_, **kwargs_: False,
        get_neighbors,
        lambda n, steps, s: visited.add(n))
    return visited


def get_components(graph: Dict[Any, List[Any]],
                   get_neighbors: Callable[..., Iterable] | None = None) -> List[Set[Any]]:
    """
    Returns a list of sets where each set is a connected component of the graph

    :param graph: Adjacency list where graph[u] = [v, ...] (u -> v)
    :param get_neighbors: A callback for getting the neighbors of the current node


    :return: List of Sets of nodes where each set is a component
    """
    if get_neighbors is None:
        get_neighbors = _get_neighbors_default

    unvisited = set(graph.keys())
    for node in graph:
        unvisited.update(get_neighbors(node, graph))

    components = []
    while unvisited:
        component = get_component_for_node(graph, next(iter(unvisited)), get_neighbors)
        components.append(component)
        unvisited -= component

    return components


def _get_neighbors_default(node: Any, graph: Dict[Any, List[Any]], *_) -> Iterable[Any]:
    for neighbor in graph.get(node, []):
        yield neighbor[0] if isinstance(neighbor, tuple) else neighbor


def _get_is_terminal_default(goal: Any) -> Callable[..., bool]:
    def is_terminal_default(node: Any, *_) -> bool:
        n = node if not isinstance(node, tuple) else node[0]
        return n == goal
    return is_terminal_default


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


def network_flow(graph: Dict[Any, List[Any]], source: Any, sink: Any) -> int:
    """
    Adapter function that transforms the standard graph representation
    into the format required by Edmonds-Karp.

    :param graph: Dict mapping node -> list of (neighbor, weight)
    :param source: Source node
    :param sink: Sink node

    :return: int representing maximum flow
    """
    # 1. Transform: Dict[Any, List[Any]] -> Dict[Any, Dict[Any, int]]
    # We create a mapping of node -> {neighbor: capacity}
    adj_map = defaultdict(dict)
    for u, neighbors in graph.items():
        for neighbor in neighbors:
            # Handle both list/tuple inputs like [v, capacity]
            if isinstance(neighbor, (list, tuple)):
                v, cap = neighbor
                adj_map[u][v] = cap
            else:
                # Handle cases where capacity might be implicit (e.g., 1)
                adj_map[u][neighbor] = 1

    # 2. Call the core algorithm
    return edmonds_karp(adj_map, source, sink, )[0]


def edmonds_karp(
    graph: Dict[Any, Dict[Any, int]],
    source: Any,
    sink: Any
) -> Tuple[int, Dict[Any, Dict[Any, int]]]:
    """
    Edmonds Karp network flow algorithm.

    :param graph: Dict mapping node -> Dict mapping neighbor -> weight
    :param source: Source node
    :param sink: Sink node

    :return: int representing maximum flow
    """
    residual = defaultdict(lambda: defaultdict(int))

    # Build residual graph
    for u, neighbors in graph.items():
        for v, cap in neighbors.items():
            residual[u][v] += cap

            # Ensure reverse edge exists
            _ = residual[v][u]

    max_flow = 0

    while True:
        parent = {source: None}
        queue = deque([source])

        while queue and sink not in parent:
            u = queue.popleft()

            for v, cap in residual[u].items():
                if cap > 0 and v not in parent:
                    parent[v] = u
                    queue.append(v)

        if sink not in parent:
            break

        # Find bottleneck
        path_flow = float("inf")
        v = sink

        while v != source:
            u = parent[v]
            path_flow = min(path_flow, residual[u][v])
            v = u

        # Update residual graph
        v = sink

        while v != source:
            u = parent[v]

            residual[u][v] -= path_flow
            residual[v][u] += path_flow

            v = u

        max_flow += path_flow

    return max_flow, residual



def min_cut(graph: Dict[Any, List[Any]], source, sink: Any) -> List[Tuple[Any, Any]]:
    """
    Return edges crossing a minimum s-t cut.

    :param graph: Dict mapping node -> Dict mapping neighbor -> weight
    :param source: Source node
    :param sink: Sink node

    :return: List of edges (u, v) forming the min cut
    """

    # Normalize into adjacency map with capacities
    adj_map = defaultdict(lambda: defaultdict(int))
    for u, neighbors in graph.items():
        for entry in neighbors:
            v, cap = (
                entry
                if isinstance(entry, (tuple, list))
                else (entry, 1)
            )

            # IMPORTANT: accumulate duplicate edges
            adj_map[u][v] += cap
    max_flow, residual = edmonds_karp(adj_map, source, sink)

    # Find vertices reachable from source in residual graph
    reachable = {source}
    queue = deque([source])

    while queue:
        u = queue.popleft()

        for v, cap in residual[u].items():
            if cap > 0 and v not in reachable:
                reachable.add(v)
                queue.append(v)

    # Every original edge from reachable -> non-reachable
    # belongs to a minimum cut
    cut_edges = []

    for u in reachable:
        for v, cap in adj_map[u].items():
            if cap > 0 and v not in reachable:
                cut_edges.append((u, v))

    return cut_edges
