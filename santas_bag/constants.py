from operator import add, mul, sub, truediv, floordiv, mod
from string import ascii_lowercase, ascii_uppercase

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

NUMS_TO_ALPHAS_LOWERCASE = {i: v for i, v in enumerate(ascii_lowercase)}
NUMS_TO_ALPHAS_UPPERCASE = {i: v for i, v in enumerate(ascii_uppercase)}
ALPHAS_TO_NUMS = {
    *{v: i for i, v in enumerate(ascii_lowercase)},
    *{v: i for i, v in enumerate(ascii_uppercase)}
}

OPS_DICT = {'+': add, '*': mul, '-': sub, '/': truediv, '//': floordiv, '%': mod, '**': pow}

REGEX_WORDS = r'\b[a-zA-Z]+\b'
REGEX_DIGITS = r'-?\d+'