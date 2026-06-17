from collections.abc import Container
from typing import Iterable, List, Callable, Dict, Tuple, Any, Set, Optional, Generator

from santas_bag.constants import CARDINAL_DIRECTIONS, ALL_DIRECTIONS
from santas_bag.search import bfs, dfs


def print_grid(grid: Iterable[Iterable], sep='', end='') -> None:
    """
    Prints a 2D grid to the console, joining elements by the specified separator.

    :param grid: The 2D structure to print.
    :param sep: String used to separate elements in a row.
    :param end: String to append after the entire grid is printed.
    """
    for row in grid:
        print(sep.join(str(i) for i in row))
    print(end=end)


def get_inbounds(grid: List[List]) -> Callable[[int, int], bool]:
    """
    Returns a closure function to check if coordinates are within the grid bounds.

    :param grid: The 2D grid context.

    :return: A function that takes (y, x) and returns True if valid.
    """
    return lambda y, x: inbounds(y, x, grid)


def inbounds(y, x: int, grid: List[List]) -> bool:
    """
    Checks if given coordinates are within the bounds of the provided grid.

    :param y: Row index.
    :param x: Column index.
    :param grid: The 2D grid to check against.

    :return: True if coordinates are valid, False otherwise.
    """
    return 0 <= y < len(grid) and 0 <= x < len(grid[y])


def grid_to_dict(grid: Iterable[Iterable]) -> Dict[Tuple[int, int], Any]:
    """
    Converts a 2D grid into a coordinate-to-value dictionary.

    :param grid: The 2D structure.

    :return: A dictionary where keys are (y, x) tuples and values are grid cells.
    """
    return {(y, x): v for y, row in enumerate(grid) for x, v in enumerate(row)}


def transpose_grid(grid: Iterable[Iterable]) -> Iterable:
    """
    Transposes a 2D grid (rows become columns and vice versa).

    :param grid: The 2D structure to transpose.

    :return: The transposed grid as a list of lists.
    """
    return [list(row) for row in zip(*grid)]


def neighbors4(y, x: int, grid: List[List]) -> List[Tuple[int, int]]:
    """
    Returns a list of valid (y, x) coordinates adjacent (cardinal) to the given point.

    :param y: Row index.
    :param x: Column index.
    :param grid: The 2D grid context.

    :return: A list of valid neighbor coordinates.
    """
    return [(y + dy, x + dx) for dx, dy in CARDINAL_DIRECTIONS if inbounds(y + dy, x + dx, grid)]


def neighbors8(y, x: int, grid: List[List]) -> List[Tuple[int, int]]:
    """
    Returns a list of valid (y, x) coordinates adjacent (including diagonals) to the point.

    :param y: Row index.
    :param x: Column index.
    :param grid: The 2D grid context.

    :return: A list of valid neighbor coordinates.
    """
    return [(y + dy, x + dx) for dx, dy in ALL_DIRECTIONS if inbounds(y + dy, x + dx, grid)]


def taxi_distance(y, x, y1, x1: int) -> int:
    """
    Calculates the Manhattan (Taxicab) distance between two points.

    :param y: Starting row.
    :param x: Starting column.
    :param y1: Target row.
    :param x1: Target column.

    :return: The calculated Manhattan distance.
    """
    return abs(y1 - y) + abs(x1 - x)


def rotate_clockwise(grid: List[List]) -> List[List]:
    """
    Rotates a grid 90 degrees clockwise.

    :param grid: The 2D grid context.

    :return: A rotated 2D grid.
    """
    return [list(row) for row in zip(*grid[::-1])]


def flip_horizontal(grid: List[List]) -> List[List]:
    """
    Flips the grid horizontally.

    :param grid: The 2D grid context.

    :return: A rotated 2D grid.
    """
    return [row[::-1] for row in grid]


def find_all_in_grid(target: Any, grid: List[List]) -> List[Tuple[int, int]]:
    """
    Returns a list of all coordinates matching the target.

    :param grid: The 2D grid context.
    :param target: The target row.

    :return: A list of coordinates matching the target.
    """
    return [(y, x) for y, row in enumerate(grid)
            for x, val in enumerate(row) if val == target]


# @TODO: test against advent of code 2023 day 10
def get_is_enclosed(
        grid: List[List],
        perimeter: Set[Tuple[int, int]],
        vertical_barriers: Container[str] = ('|', 'L', 'J')
    ) -> Callable[[int, int], bool]:
    """
    Returns a closure function to check if coordinates are within the grid bounds.

    :param grid: The 2D grid context.
    :param perimeter: The perimeter of the grid.
    :param vertical_barriers: The vertical barriers of the grid.

    :return: A function that takes (y, x) and returns True if location is enclosed within walls, False otherwise.
    """
    return lambda y, x: is_enclosed(y, x, grid, perimeter, vertical_barriers)


def is_enclosed(
        y: int,
        x: int,
        grid: List[List],
        perimeter: Set[Tuple[int, int]],
        vertical_barriers: Container[str] = ('|', 'L', 'J')
) -> bool:
    """
    Checks if a point (y, x) is enclosed by the pipe loop using horizontal ray casting.

    :param y: Row index.
    :param x: Column index.
    :param grid: The 2D grid structure.
    :param perimeter: A set of (y, x) coordinates forming the pipe loop.
    :param vertical_barriers: Characters that act as vertical walls when intersected.

    :return: True if the point is enclosed, False otherwise.
    """
    if (y, x) in perimeter:
        return False

    cross_count = 0
    # Cast a ray to the right
    for x_test in range(x + 1, len(grid[0])):
        if (y, x_test) in perimeter:
            if grid[y][x_test] in vertical_barriers:
                cross_count += 1

    return cross_count % 2 == 1


from typing import List, Tuple


def area(loop: List[Tuple[int, int]]) -> int:
    """
    Calculates the number of interior tiles using the Shoelace Formula
    and Pick's Theorem.

    :param loop: An ordered list of (y, x) coordinates forming the pipe loop.
    :return: The number of interior integer points.
    """
    # 1. Calculate the Area using the Shoelace Formula
    # Area = 0.5 * |sum(y_i * x_{i+1} - x_i * y_{i+1})|
    n = len(loop)
    area_ = 0
    for i in range(n):
        y1, x1 = loop[i]
        y2, x2 = loop[(i + 1) % n]
        area_ += (y1 * x2) - (x1 * y2)

    area_ = abs(area_) / 2

    # 2. Use Pick's Theorem: Area = I + (B / 2) - 1
    # Rearranged to solve for Interior points (I): I = Area - (B / 2) + 1
    # B is the number of integer points on the boundary (length of the loop)
    boundary_points = len(loop)
    interior_points = area_ - (boundary_points / 2) + 1

    return int(interior_points)


def _get_get_neighbors(
        impassable: Container,
        cardinal_directions: bool
) -> Callable[..., Generator[tuple[int, int], Any, None]]:
    nghbr_f = neighbors4 if cardinal_directions else neighbors8
    def get_neighbors(node, search_space, *args, **kwargs):
        y_, x_ = node
        for ny, nx in nghbr_f(y_, x_, search_space):
            if search_space[ny][nx] not in impassable:
                yield ny, nx
    return get_neighbors


def grid_bfs_from_point(
        start_y, start_x: int,
        goal: Any,
        grid: List[List],
        impassable: Container,
        cardinal_directions=True
) -> tuple[Any | None, int | float]:
    """
    Perform a breadth-first search from starting point searching for goal.

    :param start_y: Starting row index.
    :param start_x: Starting column index.
    :param grid: The 2D grid context.
    :param goal: Target value to terminate search
    :param impassable: Values that act as impassable walls.
    :param cardinal_directions: boolean flag. Use neighbors in cardinal directions if true else
                                check all 8 directions.

    :return: A tuple of ((goal_y, goal_x), steps). Returns (None, inf) if goal was not reached.
    """
    def is_terminal(node, search_space, *args, **kwargs):
        y_, x_ = node
        return search_space[y_][x_] == goal

    return bfs((start_y, start_x), grid, is_terminal, _get_get_neighbors(impassable, cardinal_directions))


def grid_bfs_from_value(
        start: Any,
        goal: Any,
        grid: List[List],
        impassable: Container,
        cardinal_directions=True
) -> tuple[Any | None, int | float]:
    """
    Perform a breadth-first search from first location of start value searching for goal.

    :param grid: The 2D grid context.
    :param start: Value from which to start searching.
    :param goal: Target value to terminate search.
    :param impassable: Values that act as impassable walls.
    :param cardinal_directions: boolean flag. Use neighbors in cardinal directions if true else
                                check all 8 directions.

    :return: A tuple of ((goal_y, goal_x), steps). Returns (None, inf) if goal was not reached.
    """
    y, x = find_all_in_grid(start, grid)[0]
    return grid_bfs_from_point(y, x, goal, grid, impassable, cardinal_directions)


# @TODO: known logical flaw in function
def grid_dfs_from_point(
        start_y, start_x: int,
        goal: Any,
        grid: List[List],
        impassable: Container,
        cardinal_directions=True
) -> tuple[Any | None, int | float]:
    """
    Perform a depth-first search from starting point searching for goal.

    :param start_y: Row index.
    :param start_x: Column index.
    :param grid: 2D grid context.
    :param impassable: Values that act as impassable walls.
    :param goal: Target value to terminate search.
    :param cardinal_directions: boolean flag. Use neighbors in cardinal directions if true (default) else
                                check all 8 directions.

    :return: A tuple of ((goal_y, goal_x), steps). Returns (None, inf) if goal was not reached.
    """
    def is_terminal(node, search_space, *args, **kwargs):
        y_, x_ = node
        return search_space[y_][x_] == goal

    nghbr_f = _get_get_neighbors(impassable, cardinal_directions)
    def get_neighbors(node, search_space, *args, **kwargs):
        neighbors = list(nghbr_f(node, search_space, *args, **kwargs))
        for n in reversed(neighbors):
            yield n

    return dfs((start_y, start_x), grid, is_terminal, get_neighbors)


def grid_dfs_from_value(
        start: Any,
        goal: Any,
        grid: List[List],
        impassable: Container,
        cardinal_directions=True
) -> tuple[Any | None, int | float]:
    """
    Perform a depth-first search from first location of start value searching for goal

    :param start: Start value to search from
    :param grid: 2D grid context.
    :param impassable: Values that act as impassable walls.
    :param goal: Target value to terminate search.
    :param cardinal_directions: boolean flag. Use neighbors in cardinal directions if true (default) else
                                check all 8 directions.

    :return: A tuple of ((goal_y, goal_x), steps). Returns (None, inf) if goal was not reached.
    """
    y, x = find_all_in_grid(start, grid)[0]

    return grid_dfs_from_point(y, x, goal, grid, impassable, cardinal_directions)


class Grid:
    def __init__(self, grid: List[List]):
        self.data = grid
        self.height = len(grid)
        self.width = len(grid[0])

    def __getitem__(self, pos):
        y, x = pos
        return self.data[y][x]

    def is_inbounds(self, y, x):
        return inbounds(y, x, self.data)
