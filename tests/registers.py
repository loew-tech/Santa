import unittest
from santas_bag.registers import *

class TestRegisters(unittest.TestCase):

    def setUp(self):
        # Create a clean state for every test
        self.regs = RegisterDictionary()
        self.ops = get_standard_ops(self.regs)

    def test_sample_execution(self):
        # Testing your custom logic flow with the new RegisterDictionary
        self.regs['a'] = 0
        self.regs['b'] = 0
        self.regs['c'] = 0

        self.ops['inc']('a')
        self.ops['dec']('b')
        self.ops['add']('c', 'a', 'b')  # c = 0 + 1 + (-1) = 0

        self.assertEqual(self.regs['a'], 1)
        self.assertEqual(self.regs['b'], -1)
        self.assertEqual(self.regs['c'], 0)

    def test_arithmetic_with_literals(self):
        """Verify that operations handle both registers and literal integers correctly."""
        self.regs['a'] = 10
        self.ops['add']('a', 5)  # 10 + 5
        self.assertEqual(self.regs['a'], 15)

        self.ops['mul']('a', 'a')  # 15 * 15
        self.assertEqual(self.regs['a'], 225)

    def test_mod_and_pow(self):
        """Verify standard operations include mod and pow."""
        self.regs['x'] = 10
        self.ops['mod']('x', 3)  # 10 % 3
        self.assertEqual(self.regs['x'], 1)

        self.ops['set']('x', 5)
        self.ops['pow']('x', 2)  # 5^2
        self.assertEqual(self.regs['x'], 25)

    def test_default_factory_behavior(self):
        """Ensure new registers auto-initialize to 0."""
        _ = self.regs['new_reg']
        self.assertEqual(self.regs.value('new_reg'), 0)

    def test_sample_execution(self):
        registers = {'a': 0, 'b': 0, 'c': 0}
        instructions = [
            Instruction('inc', ('a',)),
            Instruction('dec', ('b',)),
            Instruction('add', ('c', 'a', 'b'))
        ]

        def inc(a):
            registers[a] += 1

        def dec(a):
            registers[a] -= 1

        def add(a, b, c):
            registers[a] += registers.get(b, b) + registers.get(c, c)

        ops = {
            'inc': inc,
            'dec': dec,
            'add': add,
        }

        execute_instructions(instructions, ops)
        self.assertEqual(registers['a'], 1)
        self.assertEqual(registers['b'], -1)
        self.assertEqual(registers['c'], 0)

    def test_compile_instructions_success(self):
        def dummy_op(): pass

        instructions = [Instruction('inc', ('a',)), Instruction('dec', ('b',))]
        ops = {'inc': dummy_op, 'dec': dummy_op}

        compiled = compile_instructions(instructions, ops)
        self.assertEqual(len(compiled), 2)
        # Testing against the CompiledInstruction fields: func and args
        self.assertEqual(compiled[0].func, dummy_op)

    def test_compile_instructions_raises_error(self):
        instructions = [Instruction('unknown', ())]
        ops = {'inc': lambda: None}
        with self.assertRaises(ValueError):
            compile_instructions(instructions, ops)

    def test_instruction_jumping(self):
        """Verify the instruction pointer jumps correctly based on return value."""
        registers = {'val': 0}

        def jump_op():
            return 2

        def no_op():
            registers['val'] = 1

        instructions = [
            Instruction('jump', ()),
            Instruction('skip_me', ()),
            Instruction('target', ())
        ]
        ops = {'jump': jump_op, 'skip_me': no_op, 'target': lambda: None}

        execute_instructions(instructions, ops)
        self.assertEqual(registers['val'], 0, "Instruction should have been skipped")

    def test_execution_bounds_safety(self):
        """Ensure execution stops cleanly even if jump goes out of bounds."""
        instructions = [Instruction('out_of_bounds', ())]
        ops = {'out_of_bounds': lambda: 10}

        try:
            execute_instructions(instructions, ops)
        except Exception as e:
            self.fail(f"Execution should handle out of bounds gracefully, but raised {e}")

if __name__ == '__main__':
    unittest.main()
