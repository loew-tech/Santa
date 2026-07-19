from typing import Iterable, Mapping, Tuple, TypeVar, NamedTuple, Callable, Any

type Interval = tuple[int, int]

type Point = tuple[int, int]
type Point3D = tuple[int, int, int]

Node = TypeVar("Node")
SearchSpace = TypeVar("SearchSpace")
type Weight = int | float
type GraphNeighbor[Node] = Node | tuple[Node, Weight]
type Graph[Node] = Mapping[Node, Iterable[GraphNeighbor[Node]]]
type NeighborFunction[Node, SearchSpace] = Callable[
    [Node, SearchSpace, tuple[Any, ...], dict[str, Any]],
    Iterable[Node]
]
type TerminalFunction[Node, SearchSpace] = Callable[
    [Node, SearchSpace, tuple[Any, ...], dict[str, Any]],
    bool
]
type OnVisitFunction[Node, SearchSpace] = Callable[
    [Node, int, SearchSpace],
    None
]

type EdgeEntry = str | tuple[str, Weight]
type Edge[Node] = tuple[Node, Node]
type WeightedEdge[Node] = tuple[Node, Node, Weight]

type ResidualMap[Node] = Mapping[Node, Mapping[Node, Weight]]
type CapacityGraph[Node] = Mapping[Node, Mapping[Node, Weight]]

class Instruction(NamedTuple):
    instruction: str
    args: Tuple[Any, ...]


# The "Resolved" or "Compiled" format
class CompiledInstruction(NamedTuple):
    func: Callable[..., Any]
    args: Tuple[Any, ...]
