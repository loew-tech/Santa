# Santa's Bag

Santa's Bag is a small Python utility library for Advent of Code solutions. It bundles common helpers for grids, graphs, intervals, parsing, and generic search routines so you can focus on puzzle logic instead of reimplementing the same scaffolding each year.

## Features

- Graph utilities for adjacency-list, adjacency-matrix, and edge-list conversion
- Grid helpers for bounds checks, neighbor generation, transformations, and area calculations
- Interval helpers for overlap checks, containment checks, merging, and lookup
- Parsing helpers for extracting integers and numbers from strings and building simple parsers
- Generic search primitives for breadth-first, depth-first, and best-first traversal

## Quick start

```python
from santas_bag.utils import get_read_and_solve

# Configure once for the current year
run_day = get_read_and_solve(2024, session_id="your-aoc-session-cookie")


def part1(data):
    # 'data' is the automatically parsed input
    return sum(data)


# Run with testing=True to validate against scraped sample input
run_day(day=1, part1_func=part1, testing=True)
```

## Solve helpers

The library provides a small set of entry points whose names include `solve` and are intended for running Advent of Code solutions end to end:

- `solve(year, day, session_id, part1_func, part2_func, testing=False)` runs one or two solution functions and optionally validates them against expected answers fetched from the AoC session
- `read_and_solve(...)` performs the same orchestration, but first loads puzzle input, optionally parses it, and then runs the part 1 and part 2 handlers against that data
- `get_solve(...)` and `get_read_and_solve(...)` return closures over the above helpers so you can configure the year, session, and input paths once and reuse them across multiple days

These helpers are designed to make it easy to wire up a puzzle solution, fetch or reuse input, and run it in either normal or testing mode.

## Using the testing keyword

The solve helpers support a `testing` flag that lets you run your solution in validation mode. When `testing=True`, the helpers will try to compare your function output against the expected answer for the requested day and part.

A typical pattern looks like this:

```python
from santas_bag.utils import solve

session_id = "your-aoc-session-cookie"


def part1(data):
    return 42


def part2(data):
    return 99

solve(2024, 1, session_id, part1, part2, testing=True)
```

If your solution function accepts a `testing` keyword, it will receive that flag and can use it to switch between normal execution and test validation behavior. This is especially useful when you want the same function to run on sample input during development and then use the real puzzle input when `testing=False`.

## Caching inputs

The input-loading helpers cache puzzle input so you do not need to re-download it every time you run a solution. This helps with ettiquette towards Advent of Code scraping. When you call `read_and_solve(...)` or use one of the `get_read_and_solve(...)` wrappers, the library will look for previously saved input files and reuse them when available.

By default, inputs are stored under the project’s `inputs/` and `tests/` directories, depending on whether they are official puzzle input or sample/test input. This makes it easy to rerun solutions quickly while still allowing you to refresh the cached data when needed.

## Graph module

The graph module in `santas_bag.graph` provides utilities for working with graph data in the adjacency-list form commonly used by Advent of Code puzzles.

### Graph conversions

- `adjacency_matrix_to_dict(...)` converts an adjacency matrix into a dictionary of neighbors.
- `adjacency_lists_to_dict(...)` converts parsed adjacency-list input into a graph dictionary and can optionally add reverse edges for undirected graphs.
- `edge_list_to_dict(...)` builds a graph from an edge list, with support for weighted edges.
- `transpose_graph(...)` reverses all edges in a graph.

### Graph algorithms

- `graph_bfs(...)` and `graph_dfs(...)` run breadth-first and depth-first search directly over a graph.
- `get_in_degrees(...)` and `topological_sort(...)` support dependency-style graph workflows.
- `get_component_for_node(...)` and `get_components(...)` identify connected components.
- `spanning_tree(...)` computes a minimum spanning tree using Prim's algorithm.
- `network_flow(...)`, `edmonds_karp(...)`, and `min_cut(...)` provide basic flow and cut utilities for network-style problems.

These helpers are designed to make it easy to convert puzzle input into a graph representation and then apply common graph algorithms without reimplementing the plumbing each time.

## Parse module

The parse module in `santas_bag.parse` provides small helpers for extracting values from Advent of Code-style input strings.

### Parsing helpers

- `ints(s)` extracts all integers from a string and returns them as a list.
- `nums(s)` extracts all numeric values from a string and returns them as a list of floats.
- `range_(s, inclusive=True)` parses a string containing two integers and returns a Python `range` object.
- `interval_tuple(s)` parses a string containing two integers and returns them as an `(start, stop)` tuple.
- `get_parse_adjacency_list(...)` returns a parser function for adjacency-list input.
- `get_parse_instruction(...)` returns a parser function for simple instruction-style lines.

These helpers are handy when puzzle input needs to be converted quickly into structured values before solving the actual problem.

## Search module

The search module in `santas_bag.search` provides a reusable set of pathfinding and traversal utilities for puzzles that map naturally onto graphs or state spaces.

### Core search engine

- `search(...)` is the generic engine that drives traversal with a frontier, neighbor generator, and terminal condition.
- It supports optional callbacks such as `on_visit`, `get_state`, and `revisit`, making it flexible for pruning, logging, and custom state handling.

### Search algorithms

- `bfs(...)` performs breadth-first search for shortest paths in unweighted spaces.
- `dfs(...)` performs iterative depth-first search for exploring paths without maintaining a priority queue.
- `greedy_best_first_search(...)` uses a heuristic to prioritize promising nodes.
- `a_star(...)` is the weighted-search variant that balances path cost and heuristic estimate.
- `dijkstra(...)` is exposed as a convenience wrapper around A\* with a zero heuristic.
- `bidirectional_search(...)` searches from both the start and the goal to meet in the middle.

### Puzzle-specific helpers

- `find_all_paths(...)` collects all possible paths from a start node to a goal node.
- `solve_tsp(...)`, `solve_tsp_a_star(...)`, and `solve_tsp_optimized(...)` provide helpers for traveling-salesman-style problems.
- `floyd_warshall(...)` computes all-pairs shortest-path distances for weighted graphs.

These utilities are intended to be composed with your own graph representation or custom neighbor logic rather than tied to a specific puzzle format.

## Grid module

The grid module in `santas_bag.grid` provides a set of helpers for working with 2D puzzle grids, including coordinate checks, neighbor generation, transformations, and grid-based search.

### Grid utilities

- `print_grid(...)` prints a grid in a readable format.
- `inbounds(...)` and `get_inbounds(...)` validate whether a coordinate is inside the grid.
- `grid_to_dict(...)` converts a grid into a coordinate-to-value mapping.
- `transform_grid(...)` supports vertical flip, horizontal flip, transpose, and 90/180/270 degree rotations.
- `neighbors4(...)` and `neighbors8(...)` return cardinal or diagonal neighbors for a point.
- `taxi_distance(...)` computes Manhattan distance between two points.
- `find_all_in_grid(...)` locates every coordinate containing a given value.
- `is_enclosed(...)` and `get_is_enclosed(...)` help determine whether a point lies inside a closed loop.
- `area(...)` computes the interior area of a loop using the shoelace and pick-based approach.

### Grid search helpers

- `grid_bfs_from_point(...)` and `grid_bfs_from_value(...)` run breadth-first search from a coordinate or a value.
- `grid_dfs_from_point(...)` and `grid_dfs_from_value(...)` provide depth-first alternatives.
- `grid_find_all_paths_from_point(...)` and `grid_find_all_paths_from_value(...)` return every valid path to a goal value.
- `Grid` is a small wrapper class that stores grid data and exposes convenience methods for bounds and validity checks.

These helpers make it easy to model Advent of Code maps and mazes without rewriting the same grid traversal logic for every puzzle.

## Interval module

The interval module in `santas_bag.interval` provides lightweight helpers for working with numeric ranges represented as `(start, stop)` tuples.

### Interval operations

- `overlaps(a, b)` checks whether two intervals overlap at all.
- `contains(a, b)` checks whether one interval fully contains another.
- `merge(a, b)` returns a merged interval when two intervals overlap, otherwise `None`.
- `merge_intervals(intervals)` merges a list of overlapping intervals into a compact sorted list.
- `find_interval(intervals, value)` performs a binary search over a sorted merged interval list to find the interval that contains a target value.

These helpers are useful for range-based puzzle logic such as scheduling, scanning, or reducing overlapping segments.

## Registers module

The registers module in `santas_bag.registers` provides helpers for executing instruction lists against a register-like store, which is useful for Advent of Code problems that involve simple virtual machines or instruction-driven state machines.

### Instruction execution

- `execute_instructions(instructions, operations)` compiles and runs a list of instructions using a mapping of instruction names to callables.
- `compile_instructions(instructions, operations)` turns instruction tuples into compiled instruction objects while validating that each instruction name is known.
- `execute_compiled_instructions(compiled_instructions)` runs the compiled instructions in order, supporting jumps based on the return value of an operation.

### Register support

- `RegisterDict` provides a dictionary-backed register store with default zero values and a `value()` helper for resolving either register names or literal numbers.
- `RegisterMixin` implements the shared `value()` behavior used by the standard operations. In practice, this means a register operation can resolve either a literal number or a register name without needing special-case logic in each operation.
- `RegisterProtocol` defines the minimal interface expected by the standard operation helpers.

### Standard operations

- `get_standard_ops(registers)` returns a standard set of operations including: `inc`, `dec`, `set`, `add`, `sub`, `mul`, `mod`, `pow`, and `jmp`.

These utilities are handy when a puzzle can be modeled as a small program executed over registers and conditionals.

## Utilities module

The utilities module in `santas_bag.utils` is the high-level entry point for running Advent of Code solutions in a repeatable way. It combines input loading, output validation, timing, and wrapper helpers so you can focus on your puzzle logic.

### Solve helpers

- `solve(year, day, session_id, part1_func, part2_func, testing=False)` runs your part 1 and part 2 functions and returns their results.
- `read_and_solve(...)` loads puzzle input first, optionally parses it, and then runs the solution functions against that input.
- `get_solve(...)` and `get_read_and_solve(...)` return preconfigured closures so you can reuse the same year, session, and input paths across several days.

### Testing support

- The `testing` keyword is passed through the solve helpers so your solution functions can switch between normal execution and validation mode.
- When `testing=True`, the helpers can compare your function output with expected answers fetched from the Advent of Code session.
- This makes it easy to keep one implementation that runs on sample input during development and on real input when you want the actual answer.

These helpers are especially useful when you want a small, consistent wrapper around the logic for solving, validating, and rerunning Advent of Code puzzles.

## Installation

From the project root, install the package in editable mode:

```bash
python -m pip install -e .
```

If you want to install the runtime dependencies explicitly:

```bash
python -m pip install -r requirements.txt
```

## Module overview

- `santas_bag.graph`: graph conversion utilities and graph algorithms
- `santas_bag.grid`: 2D grid manipulation and pathfinding helpers
- `santas_bag.interval`: interval overlap and merge operations
- `santas_bag.parse`: parsing helpers for Advent of Code input
- `santas_bag.search`: reusable search engine and traversal routines
- `santas_bag.registers`: instruction and register helpers
- `santas_bag.types`: shared type aliases and data structures

## Testing

The project uses `pytest` with coverage enabled. The test suite is organized under the `tests/` package and covers the core modules for graph, grid, interval, parsing, registers, search, and utility behavior.

Run the full suite with:

```bash
pytest
```

Coverage output is included automatically via the project configuration, so you can quickly see which parts of the library are exercised by the tests.

## Notes

This package is intentionally lightweight and opinionated, making it convenient for puzzle-specific code and experiments while keeping common helpers close at hand.
