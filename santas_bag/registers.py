"""Register-machine helpers for compiling and executing instruction lists with standard register operations."""


import operator
from collections import defaultdict
from typing import Callable, Protocol, Mapping

from santas_bag.types import Instruction, CompiledInstruction


def execute_instructions(instructions: list[Instruction], operations: Mapping[str, Callable]) -> None:
    """
    Returns None. Operations executed from operations dictionary will modify registers outside function scope.
    Given a list of Instruction objects (namedtuple of the form ['instruction', 'args']) and an operations dictionary,
    execute them while instruction index is within limits of instruction list [0, len(instructions)-1].
    Instruction index increments by 1 unless the return of an operation is not None, then it increments by that value.

    :param instructions: A list of Instructions objects (namedtuple of the form ['instruction', 'args'])
    :param operations: A dictionary of closures that will operate on the registers outside the scope of this function.

    :return: None. Side effects will cause registers that operations act on to be modified
    """
    compiled = compile_instructions(instructions, operations)
    execute_compiled_instructions(compiled)


def compile_instructions(
        instructions: list[Instruction],
        operations: Mapping[str, Callable]
) -> list[CompiledInstruction]:
    """
    Returns list of CompiledInstructions objects executed from operations dictionary

    :param instructions: A list of Instructions objects (namedtuple of the form ['instruction', 'args'])
    :param operations: Operation dictionary mapping 'instruction' from an Instruction to an operation in the dict

    :raise ValueError: if an unknown instruction is passed in as an argument

    :return: List of CompiledInstructions objects
    """
    compiled = []
    for i, (instruction, args) in enumerate(instructions):
        if instruction not in operations:
            raise ValueError(f"Unknown instruction: {instruction} at index {i}")
        compiled.append(CompiledInstruction(operations[instruction], args))
    return compiled


def execute_compiled_instructions(compiled_instructions: list[CompiledInstruction]) -> None:
    """
    Returns None. Operations executed from operations dictionary will modify registers outside function scope.
    Given a list of Instruction objects (namedtuple of the form ['instruction', 'args']) and an operations dictionary,
    execute them while instruction index is within limits of instruction list [0, len(instructions)-1].
    Instruction index increments by 1 unless the return of an operation is not None, then it increments by that value.

    :param compiled_instructions: A list of CompiledConstructions to be executed while instructions index is
    in [0, len(instructions)-1]

    :return: None. Side effects will cause registers that operations act on to be modified
    """
    indx = 0
    while indx < len(compiled_instructions):
        func, args = compiled_instructions[indx]
        ret = func(*args)
        indx += 1 if ret is None else ret


class RegisterProtocol(Protocol):
    def __getitem__(self, key: str) -> int: ...

    def __setitem__(self, key: str, value: int) -> None: ...

    def value(self, key: str | int) -> int: ...


class RegisterMixin:
    """
    A mixin providing the value function used operations in get_standard_ops
    """

    def value(self, key: str | int) -> int:
        """
        Returns the value of a register or key if key is a value and not a register reference.
        :param key: the register reference or value.

        :return: the value of the referenced register or key if key is a value and not a register reference.
        """
        if isinstance(key, int):
            return key
        try:
            return int(key)
        except ValueError:
            return self[key]


class RegisterDict(defaultdict, RegisterMixin, RegisterProtocol):
    """
    A dictionary-based register storage for Virtual Machine implementations.

    This class extends `defaultdict` to provide auto-initializing integer registers
    (defaulting to 0) and incorporates `RegisterMixin` to provide the `value()`
    method for resolving register names or literal values.

    :param registers: An optional initial dictionary of register assignments.
    :param kwargs: Additional key-value pairs to initialize registers.
    """

    def __init__(self, registers: Mapping | None = None, **kwargs):
        """
        Initializes the register dictionary by merging initial data and keyword arguments.
        """
        data = {**dict(registers or {}), **kwargs}
        super().__init__(int, data)


def get_standard_ops(registers: RegisterProtocol) -> Mapping[str, Callable]:
    """
    Returns a dictionary of 'standard' operations on registers. Includes:
    inc, dec, set, add, mul, mod, and pow.

    :param registers: A register storage object satisfying the RegisterProtocol
                      (must support __getitem__, __setitem__, and value()).

    :return: A dictionary mapping operation names (strings) to their
             respective callable implementations.
    """
    val = registers.value
    set_ = registers.__setitem__

    return {
        'inc': lambda x: set_(x, val(x) + 1),
        'dec': lambda x: set_(x, val(x) - 1),
        'set': lambda x, y: set_(x, val(y)),
        'add': lambda x, y: set_(x, val(x) + val(y)),
        'sub': lambda x, y: set_(x, val(x) - val(y)),
        'mul': lambda x, y: set_(x, val(x) * val(y)),
        'mod': lambda x, y: set_(x, val(x) % val(y)),
        'pow': lambda x, y: set_(x, val(x) ** val(y)),
        'jmp': lambda x, y: val(y) if val(x) else None
    }
