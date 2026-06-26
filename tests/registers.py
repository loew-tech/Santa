import unittest

from santas_bag.registers import *

class TestRegisters(unittest.TestCase):

    def test_sample_execution(self):
        registers = {'a':0, 'b': 0, 'c': 0}
        instructions = [('inc', ('a',)),
                        ('dec', ('b',)),
                        ('add', ('c', 'a', 'b'))
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

        instruction_execution(instructions, ops)
        self.assertEqual(registers['a'], 1)
        self.assertEqual(registers['b'], -1)
        self.assertEqual(registers['c'], 0)

    def test_compile_instructions_success(self):
        def dummy_op(): pass

        instructions = [('inc', ('a',)), ('dec', ('b',))]
        ops = {'inc': dummy_op, 'dec': dummy_op}

        compiled = compile_instructions(instructions, ops)
        self.assertEqual(len(compiled), 2)
        self.assertEqual(compiled[0][0], dummy_op)

    def test_compile_instructions_raises_error(self):
        instructions = [('unknown', ())]
        ops = {'inc': lambda: None}
        with self.assertRaises(ValueError):
            compile_instructions(instructions, ops)

    def test_instruction_jumping(self):
        """Verify the instruction pointer jumps correctly based on return value."""
        registers = {'val': 0}

        # Op returns 2 to skip the next instruction
        def jump_op():
            return 2

        def no_op():
            registers['val'] = 1

        instructions = [('jump', ()), ('skip_me', ()), ('target', ())]
        ops = {'jump': jump_op, 'skip_me': no_op, 'target': lambda: None}

        instruction_execution(instructions, ops)
        self.assertEqual(registers['val'], 0, "Instruction should have been skipped")

    def test_execution_bounds_safety(self):
        """Ensure execution stops cleanly even if jump goes out of bounds."""
        instructions = [('out_of_bounds', ())]
        # Returning 10 from index 0 should exit the loop
        ops = {'out_of_bounds': lambda: 10}

        try:
            instruction_execution(instructions, ops)
        except Exception as e:
            self.fail(f"Execution should handle out of bounds gracefully, but raised {e}")


if __name__ == '__main__':
    unittest.main()
