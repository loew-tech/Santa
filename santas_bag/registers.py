from typing import Any, Callable, Dict, List, Tuple, TypeAlias

Instruction: TypeAlias = Tuple[str, Tuple[Any, ...]]
CompiledInstruction: TypeAlias = Tuple[Callable[..., Any], Tuple[Any, ...]]

# @TODO: consider this change:

# # This class gives you the readability and easy dot-access
# class Instruction(NamedTuple):
#     instruction: str
#     args: Tuple[Any, ...]
#
# # This alias keeps your function signatures clean and explicit
# CompiledInstruction: TypeAlias = Tuple[Callable[..., Any], Tuple[Any, ...]]

def instruction_execution(instructions: List[Instruction], operations: Dict[str, Callable]) -> None:
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
    compiled_instruction_execution(compiled)



def compile_instructions(
        instructions: List[Instruction],
        operations: Dict[str, Callable]
) -> List[CompiledInstruction]:
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
        compiled.append((operations[instruction], args))
    return compiled


def compiled_instruction_execution(compiled: List[CompiledInstruction]) -> None:
    """
    Returns None. Operations executed from operations dictionary will modify registers outside function scope.
    Given a list of Instruction objects (namedtuple of the form ['instruction', 'args']) and an operations dictionary,
    execute them while instruction index is within limits of instruction list [0, len(instructions)-1].
    Instruction index increments by 1 unless the return of an operation is not None, then it increments by that value.

    :param compiled: A list of CompiledConstructions to be executed while instructions index is
    in [0, len(instructions)-1]

    :return: None. Side effects will cause registers that operations act on to be modified
    """
    indx = 0
    while indx < len(compiled):
        func, args = compiled[indx]
        ret = func(*args)
        indx += 1 if ret is None else ret
