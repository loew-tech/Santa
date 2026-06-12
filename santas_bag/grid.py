from typing import Iterable, List, Callable, Dict, Tuple, Any


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