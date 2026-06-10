CARDINAL_DIRECTIONS = (
    (1, 0),
    (0, 1),
    (-1, 0),
    (0, -1),
)

DIAGONAL_DIRECTIONS = (
    (-1, -1),
    (-1, 1),
    (1, -1),
    (1, 1),
)

ALL_DIRECTIONS = (
    *CARDINAL_DIRECTIONS,
    *DIAGONAL_DIRECTIONS,
)