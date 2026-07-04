import re
from typing import List, Tuple, Callable, Union

from santas_bag.constants import REGEX_INTS, REGEX_NUMBERS
from santas_bag.registers import Instruction
from santas_bag.types import Interval


def ints(s: str) -> List[int]:
    """
    Extracts all integers from a string and returns them as a list.

    :param s: The input string containing integer-like sequences.

    :return: A list of integers found in the string.
    """
    return list(map(int, re.findall(REGEX_INTS, s)))


def nums(s: str) -> List[float]:
    """
    Extracts all numbers from a string and returns them as a list.

    :param s: The input string containing number-like sequences.

    :return: A list of numbers found in the string.
    """
    return list(map(float, re.findall(REGEX_NUMBERS, s)))


def range_(s: str, inclusive=True) -> range:
    """
    Parses a string for two integers and returns a range object.

    :param s: String containing at least two integers (start and stop).
    :param inclusive: Whether the range should include the stop value. Default is True.

    :return: A python range object.

    :raises ValueError: If fewer than two integers are found in the string.
    """
    matches = list(map(int, re.findall(REGEX_INTS, s)))
    if len(matches) < 2:
        raise ValueError("String must contain at least two integers to define a range.")
    start, stop = matches[0], matches[1]
    return range(start, stop + inclusive)


def interval_tuple(s: str) -> Interval:
    """
    Parses a string for two integers and returns a tuple (start, stop).

    :param s: String containing at least two integers (start and stop).

    :return: A tuple (start, stop)

    :raises ValueError: If fewer than two integers are found in the string.
    """
    matches = list(map(int, re.findall(REGEX_INTS, s)))
    if len(matches) < 2:
        raise ValueError("String must contain at least two integers to define a range.")
    start, stop = matches[0], matches[1]
    return start, stop


EdgeEntry = Union[str, Tuple[str, Union[int, float]]]
def get_parse_adjacency_list(
        get_vertex: Callable[[str], str],
        get_edges: Callable[[str], List[str]],
        get_weights: Callable[[str], List[Union[int, float]]] | None = None,
) -> Callable[[str], Tuple[str, List[EdgeEntry]]]:
    """
    Returns a function that parses a line and returns an EdgeEntry tuple  (Vertex followed by list of edges).

    :param get_vertex: Function that parses a line and identifies the vertex of the edge.
    :param get_edges: Function that parses a line and returns the adjacent edges.
    :param get_weights: Optional function that if provided parses a line and returns the edge weights.
                        If not provided will return list of edges without weights.

    :return: A function that parses a line and returns an EdgeEntry tuple (Vertex followed by list of edges).
    """
    def parse(line: str) -> Tuple[str, List[EdgeEntry]]:
        vertex = get_vertex(line)
        edges = get_edges(line)
        if get_weights is not None:
            weights = get_weights(line)
            return vertex, list(zip(edges, weights))
        return vertex, edges

    return parse


def _get_instruction_default(ln: str) -> str:
    return ln.split()[0]


def _get_args_default(line: str) -> Tuple:
    _, *args = line.split()
    return tuple(args)

def get_parse_instruction(
        get_instruction: Callable[[str], str] | None = None,
        get_args: Callable[[str], Tuple] | None = None,
) -> Callable[[str], Instruction]:
    """
    Returns a parse function that parses a line and returns an Instruction.

    :param get_instruction: Optional function that parses a line and returns an Instruction. Defaults to retrieving first
    entry from line.split()
    :param get_args: Optional function that parses a line and returns arguments to Instruction. Defaults to retrieving
    line.split()[1:]

    :return: Function that parses a line and returns an Instruction.
    """
    if get_instruction is None:
        get_instruction = _get_instruction_default
    if get_args is None:
        get_args = _get_args_default

    def parse(line: str) -> Instruction:
        instruction = get_instruction(line)
        args = get_args(line)
        return Instruction(instruction, args)
    return parse
