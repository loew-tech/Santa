import re
from typing import List, Tuple

from santas_bag.constants import REGEX_INTS, REGEX_NUMBERS
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
