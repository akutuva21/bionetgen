import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile
import threading

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

    @staticmethod
    def _request_file():
        request = MagicMock()
        request.data = 'dummy bngl data'
        return request

    @staticmethod
    def _write_outputs(bngl_path, output_dir, converted):
        if os.path.dirname(bngl_path) != output_dir:
            raise AssertionError('conversion path is outside its temporary directory')
        with open(bngl_path, 'r') as handle:
            converted.append((bngl_path, handle.read()))
        with open(os.path.splitext(bngl_path)[0] + '.xml', 'w') as handle:
            handle.write('<xml />')

    @staticmethod
    def _write_graph_outputs(xml_path, processed):
        processed.append(xml_path)
        with open(xml_path + '.dot', 'wb') as handle:
            handle.write(b'dummy dot')
        with open(xml_path + '.svg', 'wb') as handle:
            handle.write(b'dummy svg')

    def test_bipartite_uses_isolated_files_and_cleans_on_success(self):
        converted = []
        processed = []
        with tempfile.TemporaryDirectory() as parent:
            with patch.object(server.tempfile, 'gettempdir', return_value=parent), \
                    patch.object(server.BipartiteServer, '_bngl2xml',
                                 side_effect=lambda path, output_dir: self._write_outputs(path, output_dir, converted)), \
                    patch.object(server.createGraph, 'processBNGL',
                                 side_effect=lambda path, *args: self._write_graph_outputs(path, processed)):
                result = server.BipartiteServer().bipartite(
                    self._request_file(), 'dot', 'center', 'context', 'product')

            self.assertIsInstance(result, server.xmlrpclib.Binary)
            self.assertEqual(result.data, b'dummy dot')
            self.assertEqual(len(converted), 1)
            self.assertEqual(len(processed), 1)
            self.assertFalse(os.path.exists(os.path.dirname(converted[0][0])))
            self.assertEqual(os.listdir(parent), [])

    def test_bipartite_returns_svg_for_non_dot_requests(self):
        with tempfile.TemporaryDirectory() as parent:
            with patch.object(server.tempfile, 'gettempdir', return_value=parent), \
                    patch.object(server.BipartiteServer, '_bngl2xml',
                                 side_effect=lambda path, output_dir: self._write_outputs(path, output_dir, [])), \
                    patch.object(server.createGraph, 'processBNGL',
                                 side_effect=lambda path, *args: self._write_graph_outputs(path, [])):
                result = server.BipartiteServer().bipartite(
                    self._request_file(), 'svg', 'center', 'context', 'product')

            self.assertIsInstance(result, server.xmlrpclib.Binary)
            self.assertEqual(result.data, b'dummy svg')

    def test_bipartite_cleans_on_conversion_failure(self):
        converted = []

        def fail_conversion(path, output_dir):
            converted.append(path)
            self.assertEqual(os.path.dirname(path), output_dir)
            self.assertTrue(os.path.isfile(path))
            raise RuntimeError('conversion failed')

        with tempfile.TemporaryDirectory() as parent:
            with patch.object(server.tempfile, 'gettempdir', return_value=parent), \
                    patch.object(server.BipartiteServer, '_bngl2xml', side_effect=fail_conversion):
                with self.assertRaisesRegex(RuntimeError, 'conversion failed'):
                    server.BipartiteServer().bipartite(
                        self._request_file(), 'dot', 'center', 'context', 'product')

            self.assertEqual(len(converted), 1)
            self.assertFalse(os.path.exists(os.path.dirname(converted[0])))
            self.assertEqual(os.listdir(parent), [])

    @patch.object(server.subprocess, 'run')
    def test_bngl2xml_uses_private_output_directory_and_checks_errors(self, mock_run):
        server.BipartiteServer()._bngl2xml('/tmp/input.bngl', '/tmp/output')
        mock_run.assert_called_once_with(
            ['bngdev', '/tmp/input.bngl', '--xml', '--outdir', '/tmp/output'],
            check=True,
            shell=False)

    def test_concurrent_bipartite_requests_use_distinct_directories(self):
        converted = []
        processed = []
        lock = threading.Lock()

        def convert(path, output_dir):
            if os.path.dirname(path) != output_dir:
                raise AssertionError('conversion path is outside its temporary directory')
            with open(path, 'r') as handle:
                contents = handle.read()
            with lock:
                converted.append((path, contents))
            with open(os.path.splitext(path)[0] + '.xml', 'w') as handle:
                handle.write('<xml />')

        def process(xml_path, *args):
            with lock:
                processed.append(xml_path)
            with open(xml_path + '.dot', 'wb') as handle:
                handle.write(b'dot')
            with open(xml_path + '.svg', 'wb') as handle:
                handle.write(b'svg')

        with tempfile.TemporaryDirectory() as parent:
            with patch.object(server.tempfile, 'gettempdir', return_value=parent), \
                    patch.object(server.BipartiteServer, '_bngl2xml', side_effect=convert), \
                    patch.object(server.createGraph, 'processBNGL', side_effect=process):
                srv = server.BipartiteServer()
                with ThreadPoolExecutor(max_workers=8) as executor:
                    results = list(executor.map(
                        lambda _: srv.bipartite(
                            self._request_file(), 'dot', 'center', 'context', 'product'),
                        range(8)))

            self.assertEqual([result.data for result in results], [b'dot'] * 8)
            self.assertEqual(len(converted), 8)
            self.assertEqual(len(processed), 8)
            directories = {os.path.dirname(path) for path, _ in converted}
            self.assertEqual(len(directories), 8)
            self.assertTrue(all(not os.path.exists(path) for path in directories))
            self.assertEqual(os.listdir(parent), [])

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
