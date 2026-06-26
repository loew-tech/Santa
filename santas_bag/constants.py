from operator import add, mul, sub, truediv, floordiv, mod, eq, ne, lt, le, gt, ge
from string import ascii_lowercase, ascii_uppercase
from types import MappingProxyType

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

_ARROW_DIRECTIONS  = dict(zip('^>v<', CARDINAL_DIRECTIONS))
ARROW_DIRECTIONS = MappingProxyType(_ARROW_DIRECTIONS)

_NUMS_TO_ALPHAS_LOWERCASE = {i: v for i, v in enumerate(ascii_lowercase)}
NUMS_TO_ALPHAS_LOWERCASE = MappingProxyType(_NUMS_TO_ALPHAS_LOWERCASE)

_NUMS_TO_ALPHAS_UPPERCASE = {i: v for i, v in enumerate(ascii_uppercase)}
NUMS_TO_ALPHAS_UPPERCASE = MappingProxyType(_NUMS_TO_ALPHAS_UPPERCASE)

_ALPHAS_TO_NUMS = {
    **{v: i for i, v in enumerate(ascii_lowercase)},
    **{v: i for i, v in enumerate(ascii_uppercase)}
}
ALPHAS_TO_NUMS = MappingProxyType(_ALPHAS_TO_NUMS)

_OPS_DICT = {'+': add, '*': mul, '-': sub, '/': truediv, '//': floordiv, '%': mod, '**': pow}
OPS_DICT = MappingProxyType(_OPS_DICT)

_CONDITIONAL_OPS = {'<=': le, '>=': ge, '==': eq, '!=': ne, '<': lt, '>': gt}
CONDITIONAL_OPS = MappingProxyType(_CONDITIONAL_OPS)

REGEX_WORDS = r'\b[a-zA-Z]+\b'
REGEX_DIGITS = r'\d+'
REGEX_INTS = r'-?\d+'
REGEX_NUMBERS = r'-?\d+(?:\.\d+)?'
