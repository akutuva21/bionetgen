import unittest
from unittest.mock import patch, call
from collections import deque
import io
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the lxml dependency which is not available in the environment
import sys
from unittest.mock import MagicMock
sys.modules['lxml'] = MagicMock()
sys.modules['lxml.etree'] = MagicMock()

# Import the module to be tested
import bpgActions

class TestBpgActions(unittest.TestCase):

    def test_cleanstrings_empty_lines(self):
        """Test that empty lines are ignored."""
        input_string = "\n\n   \n\t\n"
        result = bpgActions.cleanstrings(input_string)
        self.assertEqual(result, deque())

    def test_cleanstrings_comments(self):
        """Test that lines starting with '#' are ignored."""
        input_string = "# This is a comment\n  # This is another comment\n#read_xml xyz.xml"
        result = bpgActions.cleanstrings(input_string)
        self.assertEqual(result, deque())

    def test_cleanstrings_valid_actions(self):
        """Test that valid actions are parsed correctly."""
        input_string = '''
        read_xml test.xml
        tprule A > B
        make_pairs
        make_maps
        write_elements out.txt p-t
        read_annot annot.txt
        make_flow start x y end z
        make_viz viz.js
        '''
        result = bpgActions.cleanstrings(input_string)
        expected = deque([
            ['read_xml', 'test.xml'],
            ['tprule', 'A', '>', 'B'],
            ['make_pairs'],
            ['make_maps'],
            ['write_elements', 'out.txt', 'p-t'],
            ['read_annot', 'annot.txt'],
            ['make_flow', 'start', 'x', 'y', 'end', 'z'],
            ['make_viz', 'viz.js']
        ])
        self.assertEqual(result, expected)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_cleanstrings_invalid_action(self, mock_stdout):
        """Test that an invalid action exits the program and prints an error."""
        input_string = "invalid_action arg1 arg2"

        with self.assertRaises(SystemExit):
            bpgActions.cleanstrings(input_string)

        self.assertIn("is not an action. Exiting!", mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()
