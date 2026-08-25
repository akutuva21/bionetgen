import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# Mock dependencies before import to avoid errors since this runs in a constrained environment
sys.modules['pexpect'] = MagicMock()
sys.modules['pygraphviz'] = MagicMock()
sys.modules['lxml'] = MagicMock()
sys.modules['lxml.etree'] = MagicMock()
sys.modules['readBNGXML'] = MagicMock()

# Add ContactMap to path so we can import server
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import server

class TestServer(unittest.TestCase):

    @patch('server.shutil.rmtree')
    @patch('builtins.open', new_callable=mock_open, read_data=b'dummy')
    @patch('server.createGraph')
    @patch.object(server.BipartiteServer, '_bngl2xml')
    def test_bipartite_oserror_path(self, mock__bngl2xml, mock_createGraph, mock_file, mock_rmtree):
        """
        Tests the error path in bipartite where shutil.rmtree might fail.
        With ignore_errors=True, we don't need to explicitly catch it, but we can verify it's called.
        """
        # Set up a mock bbnglFile object
        mock_bbnglFile = MagicMock()
        mock_bbnglFile.data = "dummy bngl data"

        srv = server.BipartiteServer()

        # Test bipartite with 'dot' returnType
        result = srv.bipartite(mock_bbnglFile, 'dot', 'center', 'context', 'product')

        # Verify the returned object is a Binary object as expected
        self.assertIsInstance(result, server.xmlrpclib.Binary)
        self.assertEqual(result.data, b'dummy')

        # Verify shutil.rmtree was called once
        self.assertEqual(mock_rmtree.call_count, 1)

    def test_getTransformations(self):
        """
        Tests the getTransformations method which is currently empty.
        Included to cover all untested methods.
        """
        srv = server.BipartiteServer()
        result = srv.getTransformations("dummy_file")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
