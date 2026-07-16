from typing import Tuple, List, Optional

from santas_bag.types import Interval


def overlaps(a, b: Interval) -> bool:
    """
    Returns true if a and b overlap

    :param a: interval of form (start, stop)
    :param b: interval of form (start, stop)

    :return: True if a and b overlap else False
    """
    return a[0] <= b[1] and b[0] <= a[1]


def contains(a, b: Interval) -> bool:
    """
    Returns true if a contains b

    :param a: interval of form (start, stop)
    :param b: interval of form (start, stop)

    :return: True if a contains b else False
    """
    return a[0] <= b[0] and b[1] <= a[1]


def merge(a, b: Interval) -> Optional[Interval]:
    """
    Returns a merged interval or None if intervals do not overlap

    :param a: interval of form (start, stop)
    :param b: interval of form (start, stop)

    :return: merged interval (start, stop) if a and b overlap else None
    """
    if not overlaps(a, b):
        return None

    return min(a[0], b[0]), max(a[1], b[1])

def merge_intervals(intervals: List[Interval]) -> List[Interval]:
    """
    Iteratively merge overlapping intervals in list

    :param intervals: list of intervals of form (start, stop)

    :return: List of merged intervals of the form (start, stop)
    """
    intervals = sorted(intervals)

    merged = []
    for interval in intervals:
        start, end = interval[0], interval[-1]
        if not merged:
            merged.append([start, end])
            continue

        last_start, last_end = merged[-1]
        if start <= last_end + 1:
            merged[-1][-1] = max(last_end, end)
        else:
            merged.append([start, end])

    return [(i[0], i[1]) for i in merged]


def find_interval(intervals: List[Interval], value: int) -> Optional[Interval]:
    """
    Given a list of sorted, merged intervals, returns the interval that contains value

    :param intervals: list of intervals of form (start, stop)
    :param value: the target value to find

    :return: Interval of the form (start, stop) that contains value or None if no such interval exists
    """
    left, right = 0, len(intervals) - 1
    while left <= right:
        mid = (left + right) // 2
        start, end = intervals[mid]
        if start <= value <= end:
            return intervals[mid]

        if value < start:
            right = mid - 1
        else:
            left = mid + 1
    return None
