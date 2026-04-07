import unittest
import sys
import os

from unittest.mock import patch, MagicMock

# Mock dependencies to avoid importing them and failing in a headless environment
sys.modules['readBNGXML'] = MagicMock()
sys.modules['networkx'] = MagicMock()

# Add the parent directory to sys.path to resolve 'collapsedContactMap' import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from collapsedContactMap import getMapping

class TestGetMapping(unittest.TestCase):
    def test_getMapping_simple(self):
        # mapp is a list of tuples or lists
        mapp = [('site1', 'site2'), ('site3', 'site4')]
        result = getMapping(mapp, 'site1')
        self.assertEqual(result, 'site2')

    def test_getMapping_not_found(self):
        mapp = [('site1', 'site2'), ('site3', 'site4')]
        result = getMapping(mapp, 'site5')
        self.assertIsNone(result)

    def test_getMapping_multiple_elements(self):
        mapp = [('site1', 'site2', 'site3')]
        result = getMapping(mapp, 'site1')
        self.assertEqual(result, 'site2') # Returns the first element that is not 'site1'

    def test_getMapping_empty_mapp(self):
        result = getMapping([], 'site1')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
