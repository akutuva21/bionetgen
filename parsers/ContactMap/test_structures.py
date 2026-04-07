import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from structures import parseReactions

class TestParseReactions(unittest.TestCase):
    def test_parseReactions_happy_path(self):
        """Test parseReactions with a standard reaction string containing states and bonds."""
        result = parseReactions("A(b!1,p~P).B(a!1)")
        # Expected from actual pyparsing output
        self.assertEqual(len(result), 2)

        # 'A(b!1,p~P)'
        self.assertEqual(result[0][0], 'A')
        self.assertEqual(result[0][1][0], 'b')
        self.assertEqual(result[0][1][1][0], '!')
        self.assertEqual(result[0][1][1][1], '1')
        self.assertEqual(result[0][2][0], 'p')
        self.assertEqual(result[0][2][1][0], '~')
        self.assertEqual(result[0][2][1][1], 'P')

        # 'B(a!1)'
        self.assertEqual(result[1][0], 'B')
        self.assertEqual(result[1][1][0], 'a')
        self.assertEqual(result[1][1][1][0], '!')
        self.assertEqual(result[1][1][1][1], '1')

    def test_parseReactions_simple_molecule(self):
        """Test parseReactions with a simple molecule string without components.
        The grammar requires either 'Molecule(component)' or 'Molecule(component,component)'.
        Actually, looking at the code:
        components = (Word(alphanums + "_") + ...)
        molecule = (Word(...) + Optional(Suppress('(')) + Group(components) + ...)
        So the grammar *requires* at least one component if we look closely, or does it?
        Let's test with a valid structure.
        """
        result = parseReactions("A(b)")
        self.assertEqual(result, [['A', ['b']]])

    def test_parseReactions_empty_string(self):
        """Test parseReactions with an empty string. Should raise an exception."""
        from pyparsing import ParseException
        with self.assertRaises(ParseException):
             parseReactions("")

if __name__ == '__main__':
    unittest.main()
