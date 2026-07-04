import unittest

from santas_bag.parse import *

class TestParse(unittest.TestCase):

    def test_ints(self):
        self.assertEqual([10, 20, 30], ints("10, 20, 30"))
        self.assertEqual([-5, 100], ints("The values are -5 and 100"))
        self.assertEqual([], ints("No numbers here"))

    def test_nums(self):
        self.assertEqual([3.14, 10.0], nums("3.14 and 10"))
        self.assertEqual([-0.5, 1.5], nums("Negative -0.5 and positive 1.5"))

    def test_range_inclusive(self):
        r = range_("1 to 5", inclusive=True)
        self.assertEqual([1, 2, 3, 4, 5], list(r))

    def test_range_exclusive(self):
        r = range_("1 to 5", inclusive=False)
        self.assertEqual([1, 2, 3, 4], list(r))

    def test_range_error(self):
        with self.assertRaises(ValueError):
            range_("Just one number 5")

    def test_interval_exclusive(self):
        r = interval_tuple("1 to 5")
        self.assertEqual(1, r[0])
        self.assertEqual(5, r[1])

    def test_interval_error(self):
        with self.assertRaises(ValueError):
            interval_tuple("Just one number 5")

    def test_get_parse_adjacency_list_unweighted(self):
        """Test parsing of a simple vertex:edge1,edge2 list."""
        get_v = lambda line: line.split(':')[0]
        get_e = lambda line: line.split(':')[1].split(',')

        parse = get_parse_adjacency_list(get_v, get_e)
        vertex, edges = parse("A:B,C")

        self.assertEqual(vertex, "A")
        self.assertEqual(edges, ["B", "C"])

    def test_get_parse_adjacency_list_weighted(self):
        """Test parsing where edge weights are provided."""
        get_v = lambda line: line.split(':')[0]
        get_e = lambda line: line.split(':')[1].split(',')
        get_w = lambda line: [int(w) for w in line.split(':')[2].split(',')]

        parse = get_parse_adjacency_list(get_v, get_e, get_w)
        vertex, edges = parse("A:B,C:10,20")

        self.assertEqual(vertex, "A")
        self.assertEqual(edges, [("B", 10), ("C", 20)])

    def test_get_parse_adjacency_list_empty(self):
        """Ensure no edges result in an empty list."""
        parse = get_parse_adjacency_list(lambda l: l, lambda l: [])
        vertex, edges = parse("StandaloneVertex")
        self.assertEqual(edges, [])

    def test_get_parse_instruction_default(self):
        # Use default getters
        parse_func = get_parse_instruction()

        # Execute and Verify
        instr = parse_func("ADD a b")
        self.assertEqual(instr.instruction, "ADD")
        self.assertEqual(instr.args, ('a', 'b'))
        self.assertIsInstance(instr, Instruction)

    def test_get_parse_instruction(self):
        # Setup: Define simple extraction logic for a custom format
        # Format: "OP:ARG1,ARG2"
        def get_op(line):
            return line.split(':')[0]

        def get_args(line):
            args_str = line.split(':')[1]
            return tuple(args_str.split(','))

        # Create the parser
        parse_func = get_parse_instruction(get_op, get_args)

        # Execute and Verify
        instr = parse_func("ADD:a,b")
        self.assertEqual(instr.instruction, "ADD")
        self.assertEqual(instr.args, ('a', 'b'))
        self.assertIsInstance(instr, Instruction)

    def test_get_parse_instruction_with_complex_logic(self):
        # Setup: Complex logic where arguments need casting
        def get_op(line):
            return line.split()[0]

        def get_args(line):
            # Parse "INC 5" -> (5,)
            return (int(line.split()[1]),)

        parse_func = get_parse_instruction(get_op, get_args)

        instr = parse_func("INC 5")
        self.assertEqual(instr.instruction, "INC")
        self.assertEqual(instr.args, (5,))
        self.assertIsInstance(instr.args[0], int)

if __name__ == '__main__':
    unittest.main()
