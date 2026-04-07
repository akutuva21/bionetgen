import unittest
import sys
import os
import unittest.mock

# Create a mock for networkx
sys.modules['networkx'] = unittest.mock.MagicMock()

# Create a mock for readBNGXML to bypass its Python 2 syntax errors
sys.modules['readBNGXML'] = unittest.mock.MagicMock()

# Now we can import the module we want to test
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from collapsedContactMap import getMapping

class TestGetMapping(unittest.TestCase):
    def test_getMapping_basic(self):
        """Test standard retrieval of mapped values in 2-element tuples/lists."""
        mapp = [['A', 'B'], ['C', 'D']]
        self.assertEqual(getMapping(mapp, 'A'), 'B')
        self.assertEqual(getMapping(mapp, 'B'), 'A')
        self.assertEqual(getMapping(mapp, 'C'), 'D')
        self.assertEqual(getMapping(mapp, 'D'), 'C')

    def test_getMapping_multiple_elements(self):
        """Test with >2 elements, ensuring it returns the first element that isn't the queried site."""
        mapp = [['A', 'B', 'C']]
        # getMapping returns the first element that is not the site
        self.assertEqual(getMapping(mapp, 'A'), 'B')
        self.assertEqual(getMapping(mapp, 'B'), 'A')
        self.assertEqual(getMapping(mapp, 'C'), 'A')

    def test_getMapping_not_found(self):
        """Test with a site that doesn't exist in the mapping."""
        mapp = [['A', 'B']]
        self.assertIsNone(getMapping(mapp, 'C'))

    def test_getMapping_empty_mapping(self):
        """Test with an empty list mapping."""
        mapp = []
        self.assertIsNone(getMapping(mapp, 'A'))

if __name__ == '__main__':
    unittest.main()
