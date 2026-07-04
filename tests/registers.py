import unittest
from santas_bag.registers import *

class TestRegisters(unittest.TestCase):

    def setUp(self):
        # Create a clean state for every test
        self.regs = RegisterDict()
        self.ops = get_standard_ops(self.regs)

    def test_sample_execution(self):
        # Testing your custom logic flow with the new RegisterDict
        self.regs['a'] = 0
        self.regs['b'] = 0
        self.regs['c'] = 0

        self.ops['inc']('a')
        self.ops['dec']('b')
        self.ops['add']('c', 1)  # c = 0 + 1 = 1

        self.assertEqual(1, self.regs['a'])
        self.assertEqual(-1, self.regs['b'])
        self.assertEqual(1, self.regs['c'])

    def test_arithmetic_with_literals(self):
        """Verify that operations handle both registers and literal integers correctly."""
        self.regs['a'] = 10
        self.ops['add']('a', 5)  # 10 + 5
        self.assertEqual(15, self.regs['a'])

        self.ops['mul']('a', 'a')  # 15 * 15
        self.assertEqual(225, self.regs['a'])

    def test_mod_and_pow(self):
        """Verify standard operations include mod and pow."""
        self.regs['x'] = 10
        self.ops['mod']('x', 3)  # 10 % 3
        self.assertEqual(1, self.regs['x'])

        self.ops['set']('x', 5)
        self.ops['pow']('x', 2)  # 5^2
        self.assertEqual(25, self.regs['x'])

    def test_sub(self):
        """Verify the sub operation performs subtraction."""
        self.regs['a'] = 10
        self.regs['b'] = 4
        self.ops['sub']('a', 'b')
        self.assertEqual(6, self.regs['a'])

    def test_jmp(self):
        """Verify the jmp operation returns the jump offset or None."""
        # Condition is true (a=1), should return value of y (5)
        self.regs['a'] = 1
        self.regs['b'] = 5
        result = self.ops['jmp']('a', 'b')
        self.assertEqual(5, result)

        # Condition is false (a=0), should return None
        self.regs['a'] = 0
        result = self.ops['jmp']('a', 'b')
        self.assertEqual(None, result)

    def test_default_factory_behavior(self):
        """Ensure new registers auto-initialize to 0."""
        _ = self.regs['new_reg']
        self.assertEqual(0, self.regs.value('new_reg'))

    def test_compile_instructions_success(self):
        def dummy_op(): pass

        instructions = [Instruction('inc', ('a',)), Instruction('dec', ('b',))]
        ops = {'inc': dummy_op, 'dec': dummy_op}

        compiled = compile_instructions(instructions, ops)
        self.assertEqual(2, len(compiled))
        # Testing against the CompiledInstruction fields: func and args
        self.assertEqual(dummy_op, compiled[0].func)

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
        self.assertEqual(0, registers['val'] )

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
