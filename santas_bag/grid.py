from typing import Iterable, List, Callable, Dict, Tuple, Any

from santas_bag.constants import CARDINAL_DIRECTIONS, ALL_DIRECTIONS


def print_grid(grid: Iterable[Iterable], sep='', end='') -> None:
    for row in grid:
        print(sep.join(str(i) for i in row))
    print(end=end)


def get_inbounds(grid: List[List]) -> Callable[[int, int], bool]:
    return lambda y, x: inbounds(y, x, grid)


def inbounds(y, x: int, grid: List[List]) -> bool:
    return 0 <= y < len(grid) and 0 <= x < len(grid[y])


def grid_to_dict(grid: Iterable[Iterable]) -> Dict[Tuple[int, int], Any]:
    return {(y, x): v for y, row in enumerate(grid) for x, v in enumerate(row)}


def transpose_grid(grid: Iterable[Iterable]) -> Iterable:
    return [list(row) for row in zip(*grid)]


def neighbors4(y, x: int, grid: List[List]) -> List[Tuple[int, int]]:
    return [(y + dy, x + dx) for dx, dy in CARDINAL_DIRECTIONS if inbounds(y + dy, x + dx, grid)]


def neighbors8(y, x: int, grid: List[List]) -> List[Tuple[int, int]]:
    return [(y + dy, x + dx) for dx, dy in ALL_DIRECTIONS if inbounds(y + dy, x + dx, grid)]
