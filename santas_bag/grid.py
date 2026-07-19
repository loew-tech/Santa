"""Grid helpers for bounds checks, neighbor generation, transformations, enclosed-area calculations, and grid-based traversal."""


from collections.abc import Container
from collections.abc import Callable, Mapping, Iterable
from typing import Any, Literal

from santas_bag.constants import CARDINAL_DIRECTIONS, ALL_DIRECTIONS
from santas_bag.search import bfs, dfs
from santas_bag.types import Point, NeighborFunction


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


def get_inbounds(grid: list[list]) -> Callable[[int, int], bool]:
    """
    Returns a closure function to check if coordinates are within the grid bounds.

    :param grid: The 2D grid context.

    :return: A function that takes (y, x) and returns True if valid.
    """
    return lambda y, x: inbounds(grid, y, x)


def inbounds(grid: list[list], y, x: int) -> bool:
    """
    Checks if given coordinates are within the bounds of the provided grid.

    :param grid: The 2D grid to check against.
    :param y: Row index.
    :param x: Column index.

    :return: True if coordinates are valid, False otherwise.
    """
    return 0 <= y < len(grid) and 0 <= x < len(grid[y])


def grid_to_dict(grid: Iterable[Iterable]) -> Mapping[Point, Any]:
    """
    Converts a 2D grid into a coordinate-to-value dictionary.

    :param grid: The 2D structure.

    :return: A dictionary where keys are (y, x) tuples and values are grid cells.
    """
    return {(y, x): v for y, row in enumerate(grid) for x, v in enumerate(row)}


def transform_grid(grid: Iterable[Iterable],
                   mode: Literal['v_flip', 'h_flip', 'transpose', 'rot90', 'rot180', 'rot270']) -> list[list]:
    """
    Performs various geometric transformations on a 2D grid.

    :param grid: The 2D structure.
    :param mode: The transformation mode.

    Modes:
    - 'v_flip': Vertical flip (top-to-bottom)
    - 'h_flip': Horizontal flip (left-to-right)
    - 'transpose': Rows become columns
    - 'rot90': 90 degrees clockwise
    - 'rot180': 180 degrees clockwise
    - 'rot270': 270 degrees clockwise

    :return: The transformed 2D grid.
    """
    g = [list(row) for row in grid]

    match mode:
        case 'v_flip':
            return g[::-1]
        case 'h_flip':
            return [row[::-1] for row in g]
        case 'transpose':
            return [list(row) for row in zip(*g)]
        case 'rot90':
            return [list(row) for row in zip(*g[::-1])]
        case 'rot180':
            return [row[::-1] for row in g[::-1]]
        case 'rot270':
            return [list(row) for row in zip(*g)][::-1]
        case _:
            raise ValueError(f"Unknown transformation mode: {mode}")

def neighbors4(y, x: int, grid: list[list]) -> list[Point]:
    """
    Returns a list of valid (y, x) coordinates adjacent (cardinal) to the given point.

    :param y: Row index.
    :param x: Column index.
    :param grid: The 2D grid context.

    :return: A list of valid neighbor coordinates.
    """
    return [(y + dy, x + dx) for dx, dy in CARDINAL_DIRECTIONS if inbounds(grid, y + dy, x + dx)]


def neighbors8(y, x: int, grid: list[list])-> list[Point]:
    """
    Returns a list of valid (y, x) coordinates adjacent (including diagonals) to the point.

    :param y: Row index.
    :param x: Column index.
    :param grid: The 2D grid context.

    :return: A list of valid neighbor coordinates.
    """
    return [(y + dy, x + dx) for dx, dy in ALL_DIRECTIONS if inbounds(grid, y + dy, x + dx)]


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


def find_all_in_grid(grid: list[list], target: Any) -> list[Point]:
    """
    Returns a list of all coordinates matching the target.

    :param grid: The 2D grid context.
    :param target: The target row.

    :return: A list of coordinates matching the target.
    """
    return [(y, x) for y, row in enumerate(grid)
            for x, val in enumerate(row) if val == target]


def get_is_enclosed(
        grid: list[list],
        perimeter: set[Point],
        vertical_barriers: Container[str] = ('|', 'L', 'J')
    ) -> Callable[[int, int], bool]:
    """
    Returns a closure function to check if coordinates are within the grid bounds.

    :param grid: The 2D grid context.
    :param perimeter: The perimeter of the grid.
    :param vertical_barriers: The vertical barriers of the grid.

    :return: A function that takes (y, x) and returns True if location is enclosed within walls, False otherwise.
    """
    return lambda y, x: is_enclosed(grid, perimeter, y, x, vertical_barriers)


def is_enclosed(
        grid: list[list],
        perimeter: set[Point],
        y: int,
        x: int,
        vertical_barriers: Container[str] = ('|', 'L', 'J')
) -> bool:
    """
    Checks if a point (y, x) is enclosed by the pipe loop using horizontal ray casting.

    :param grid: The 2D grid structure.
    :param perimeter: A set of (y, x) coordinates forming the pipe loop.
    :param y: Row index.
    :param x: Column index.
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


def area(loop: list[Point]) -> int:
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


def _get_get_neighbors_default(
        impassable: Container,
        cardinal_directions: bool
) -> NeighborFunction[Point, list[list]]:
    nghbr_f = neighbors4 if cardinal_directions else neighbors8
    def get_neighbors(node, search_space, *_):
        y_, x_ = node
        for ny, nx in nghbr_f(y_, x_, search_space):
            if search_space[ny][nx] not in impassable:
                yield ny, nx
    return get_neighbors


def grid_bfs_from_point(
        grid: list[list],
        start_y, start_x: int,
        goal: Any,
        impassable: Container=(),
        cardinal_directions=True
) -> tuple[Any | None, int | float]:
    """
    Perform a breadth-first search from starting point searching for goal.

    :param start_y: Starting row index.
    :param start_x: Starting column index.
    :param grid: The 2D grid context.
    :param goal: Target value to terminate search
    :param impassable: Values that act as impassable walls.
    :param cardinal_directions: boolean flag. Use neighbors in cardinal directions if true else check all 8 directions.

    :return: A tuple of ((goal_y, goal_x), steps). Returns (None, inf) if goal was not reached.
    """
    def is_terminal(node, search_space, *_):
        y_, x_ = node
        return search_space[y_][x_] == goal

    return bfs((start_y, start_x), grid, _get_get_neighbors_default(impassable, cardinal_directions), is_terminal)


def grid_bfs_from_value(
        grid: list[list],
        start: Any,
        goal: Any,
        impassable: Container=(),
        cardinal_directions=True
) -> tuple[Any | None, int | float]:
    """
    Perform a breadth-first search from first location of start value searching for goal.

    :param grid: The 2D grid context.
    :param start: Value to search from first location of
    :param goal: Target value to terminate search.
    :param impassable: Values that act as impassable walls.
    :param cardinal_directions: boolean flag. Use neighbors in cardinal directions if true else check all 8 directions.

    :return: A tuple of ((goal_y, goal_x), steps). Returns (None, inf) if goal was not reached.
    """
    y, x = find_all_in_grid(grid, start)[0]
    return grid_bfs_from_point(grid, y, x, goal, impassable, cardinal_directions)


def grid_dfs_from_point(grid: list[list],
                        start_y, start_x: int,
                        goal: Any,
                        impassable: Container=(),
                        cardinal_directions=True) -> tuple[Any | None, int | float]:
    """
    Perform a depth-first search from starting point searching for goal.

    :param start_y: Row index.
    :param start_x: Column index.
    :param grid: 2D grid context.
    :param impassable: Values that act as impassable walls.
    :param goal: Target value to terminate search.
    :param cardinal_directions: boolean flag. Use neighbors in cardinal directions if true (default) else check all 8 directions.

    :return: A tuple of ((goal_y, goal_x), steps). Returns (None, inf) if goal was not reached.
    """
    def is_terminal(node, search_space, *_):
        y_, x_ = node
        return search_space[y_][x_] == goal

    nghbr_f = _get_get_neighbors_default(impassable, cardinal_directions)
    def get_neighbors(node, search_space, *args, **kwargs):
        neighbors = list(nghbr_f(node, search_space, *args, **kwargs))
        for n in reversed(neighbors):
            yield n

    return dfs((start_y, start_x), grid, get_neighbors, is_terminal)


def grid_dfs_from_value(
        grid: list[list],
        start: Any,
        goal: Any,
        impassable: Container=(),
        cardinal_directions=True
) -> tuple[Any | None, int | float]:
    """
    Perform a depth-first search from first location of start value searching for goal

    :param start: Value to search from first location of
    :param grid: 2D grid context.
    :param impassable: Values that act as impassable walls.
    :param goal: Target value to terminate search.
    :param cardinal_directions: boolean flag. Use neighbors in cardinal directions if true (default) else check all 8 directions.

    :return: A tuple of ((goal_y, goal_x), steps). Returns (None, inf) if goal was not reached.
    """
    y, x = find_all_in_grid(grid, start)[0]

    return grid_dfs_from_point(grid, y, x, goal, impassable, cardinal_directions)


def grid_find_all_paths_from_point(
        grid: list[list],
        start_y: int, start_x: int,
        goal: Any,
        impassable: Container=(),
        cardinal_directions=True
) -> list[list[Point]]:
    """
    Finds all paths from a starting point to a goal value in the grid.

    :param start_y: Row index.
    :param start_x: Column index.
    :param goal: Target value to terminate search.
    :param grid: 2D grid context.
    :param impassable: Values that act as impassable walls.
    :param cardinal_directions: boolean flag. Use neighbors in cardinal directions if true (default) else check all 8 directions.

    :return: A list of paths, where each path is a list of (y, x) coordinates.
    """
    all_paths = []
    nghbr_f = neighbors4 if cardinal_directions else neighbors8

    def find_paths(current_node, current_path):
        y, x = current_node

        if grid[y][x] == goal:
            all_paths.append(list(current_path))
            return

        for ny, nx in nghbr_f(y, x, grid):
            if grid[ny][nx] not in impassable and (ny, nx) not in current_path:
                current_path.append((ny, nx))
                find_paths((ny, nx), current_path)
                current_path.pop()  # Backtrack

    find_paths((start_y, start_x), [(start_y, start_x)])
    return all_paths


def grid_find_all_paths_from_value(
        grid: list[list],
        start: Any,
        goal: Any,
        impassable: Container=(),
        cardinal_directions=True
) -> list[list[Point]]:
    """
    Finds all paths from a starting point to a goal value in the grid.

    :param start: Value to search from first location of
    :param goal: Target value to terminate search.
    :param grid: 2D grid context.
    :param impassable: Values that act as impassable walls.
    :param cardinal_directions: boolean flag. Use neighbors in cardinal directions if true (default) else check all 8 directions.

    :return: A list of paths, where each path is a list of (y, x) coordinates.
    """
    y, x = find_all_in_grid(grid, start)[0]
    return grid_find_all_paths_from_point(grid, y, x, goal, impassable, cardinal_directions)


class Grid:
    def __init__(self, grid: list[list], impassable: Container | None = None):
        self.data = grid
        self.height = len(grid)
        self.width = len(grid[0])
        self.impassable = impassable if impassable is not None else set()

    def __getitem__(self, pos: Point) -> Any:
        y, x = pos
        return self.data[y][x]

    def is_inbounds(self, y, x: int) -> bool:
        return inbounds(self.data, y, x)

    def is_valid(self, y, x: int) -> bool:
        return self.is_inbounds(y, x) and self.data[y][x] not in self.impassable
