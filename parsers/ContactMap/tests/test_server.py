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
        Tests the error path in bipartite where shutil.rmtree might throw an OSError,
        though we pass ignore_errors=True so it should just gracefully ignore it.
        """
        # Make shutil.rmtree raise an OSError to simulate what would happen if ignore_errors wasn't passed,
        # but realistically ignore_errors=True masks it inside rmtree.
        # So we'll just check if it gets called properly.

        # Set up a mock bbnglFile object
        mock_bbnglFile = MagicMock()
        mock_bbnglFile.data = "dummy bngl data"

        srv = server.BipartiteServer()

        result = srv.bipartite(mock_bbnglFile, 'dot', 'center', 'context', 'product')

        self.assertIsInstance(result, server.xmlrpclib.Binary)
        self.assertEqual(result.data, b'dummy')

        mock_rmtree.assert_called_once()
        self.assertTrue(mock_rmtree.call_args[1].get('ignore_errors', False))

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
