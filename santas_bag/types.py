from typing import Iterable, Mapping, Tuple, TypeAlias, TypeVar, NamedTuple

type Interval = tuple[int, int]
type Point = tuple[int, int]
type Point3D = tuple[int, int, int]

Node = TypeVar("Node")
type Weight = int | float
type GraphNeighbor[Node] = Node | Tuple[Node, Weight]
type Graph[Node] = Mapping[Node, Iterable[GraphNeighbor[Node]]]


class Edge[Node](NamedTuple):
    u: Node
    v: Node

class WeightedEdge[Node](NamedTuple):
    u: Node
    v: Node
    weight: Weight

type ResidualMap[Node] = Mapping[Node, Mapping[Node, Weight]]
type CapacityGraph[Node] = Mapping[Node, Mapping[Node, Weight]]
