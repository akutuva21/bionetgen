import unittest
import sys
import os
from unittest.mock import patch, mock_open, MagicMock

# Mock external dependencies like lxml which are missing in the environment
sys.modules['lxml'] = MagicMock()
sys.modules['lxml.etree'] = MagicMock()
sys.modules['pyparsing'] = MagicMock()
sys.modules['networkx'] = MagicMock()
sys.modules['pygraphviz'] = MagicMock()

# Add parent directory to path so we can import modules correctly if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from collections import deque

import bpgActions
from bpgActions import cleanstrings, processActions

class TestBpgActions(unittest.TestCase):

    def test_cleanstrings_valid(self):
        input_str = "read_xml file.xml\nmake_pairs\nmake_maps"
        result = cleanstrings(input_str)
        self.assertEqual(len(result), 3)
        self.assertEqual(list(result[0]), ["read_xml", "file.xml"])
        self.assertEqual(list(result[1]), ["make_pairs"])
        self.assertEqual(list(result[2]), ["make_maps"])

    def test_cleanstrings_comments_and_empty(self):
        input_str = "# this is a comment\n\nread_xml file.xml\n  \n# another comment\nmake_maps"
        result = cleanstrings(input_str)
        self.assertEqual(len(result), 2)
        self.assertEqual(list(result[0]), ["read_xml", "file.xml"])
        self.assertEqual(list(result[1]), ["make_maps"])

    @patch('builtins.exit')
    @patch('builtins.print')
    def test_cleanstrings_invalid_action(self, mock_print, mock_exit):
        input_str = "invalid_action arg1"
        cleanstrings(input_str)
        mock_print.assert_called_once()
        mock_exit.assert_called_once()

    @patch('bpgModel.getAtomizedRules')
    @patch('bpgModel.getElements')
    @patch('os.path.isfile')
    def test_processActions_read_xml(self, mock_isfile, mock_getElements, mock_getAtomizedRules):
        mock_isfile.return_value = True
        mock_getAtomizedRules.return_value = "rules"
        mock_getElements.return_value = (["patterns"], ["transformations"])

        input_str = "read_xml file.xml"

        processActions(input_str)

        mock_isfile.assert_called_with("file.xml")
        mock_getAtomizedRules.assert_called_with("file.xml")
        mock_getElements.assert_called_with("rules")

    @patch('builtins.print')
    def test_processActions_invalid_command(self, mock_print):
        # We need to mock cleanstrings directly or bypass it because cleanstrings will exit
        # But wait, invalid commands are caught in cleanstrings. So processActions won't even
        # reach the `else` branch for invalid commands if we pass it a string!
        # Ah, the `else` branch in `processActions` might be unreachable unless `cleanstrings`
        # `available` list is updated but not `processActions`.
        # Let's test it by mocking `cleanstrings`
        with patch('bpgActions.cleanstrings') as mock_clean:
            mock_clean.return_value = deque([["unknown_cmd"]])
            processActions("unknown_cmd")
            mock_print.assert_called_with("Command not found: unknown_cmd")

    @patch('bpgModel.getAtomizedRules')
    @patch('bpgModel.getElements')
    @patch('bpgMaps.getTransformationPairs')
    @patch('os.path.isfile')
    def test_processActions_tprule_and_make_pairs(self, mock_isfile, mock_getTransPairs, mock_getElements, mock_getRules):
        mock_isfile.return_value = True
        mock_getRules.return_value = "rules"
        mock_getElements.return_value = (["patterns"], ["transformations"])
        mock_getTransPairs.return_value = (["tp"], ["ir"])

        input_str = "read_xml file.xml\ntprule a > b\ntprule c < d\nmake_pairs"
        processActions(input_str)

        # Check that getTransformationPairs was called with the right tprules
        mock_getTransPairs.assert_called_once_with(["transformations"], [['a', 'b'], ['d', 'c']])

    @patch('bpgModel.getAtomizedRules')
    @patch('bpgModel.getElements')
    @patch('bpgMaps.getTransformationPairs')
    @patch('bpgMaps.getNameDictionary')
    @patch('os.path.isfile')
    @patch('builtins.open', new_callable=mock_open)
    def test_processActions_write_elements(self, mock_file, mock_isfile, mock_getNameDict, mock_getTransPairs, mock_getElements, mock_getRules):
        mock_isfile.return_value = True
        mock_getRules.return_value = ["rule1"]
        mock_getElements.return_value = (["patt1"], ["trans1"])
        mock_getTransPairs.return_value = (["tp1"], ["ir1"])
        mock_getNameDict.return_value = "names"

        # Test full flow to write_elements
        input_str = "read_xml file.xml\nmake_pairs\nwrite_elements out.txt p-t-tp-ir-r"
        processActions(input_str)

        mock_file.assert_called_with("out.txt", 'w')
        handle = mock_file()

        # Instead of checking exactly the string written, we can verify write was called
        self.assertTrue(handle.write.called)

    @patch('bpgModel.getAtomizedRules')
    @patch('bpgModel.getElements')
    @patch('bpgMaps.getTransformationPairs')
    @patch('bpgMaps.getNameDictionary')
    @patch('bpgMaps.getMaps')
    @patch('os.path.isfile')
    def test_processActions_make_maps(self, mock_isfile, mock_getMaps, mock_getNameDict, mock_getTransPairs, mock_getElements, mock_getRules):
        mock_isfile.return_value = True
        mock_getRules.return_value = ["rule1"]
        mock_getElements.return_value = (["patt1"], ["trans1"])
        mock_getTransPairs.return_value = (["tp1"], ["ir1"])
        mock_getNameDict.return_value = "names"
        mock_getMaps.return_value = "maps"

        input_str = "read_xml file.xml\nmake_pairs\nmake_maps"
        processActions(input_str)

        mock_getMaps.assert_called_with("names", 0)

    @patch('bpgModel.getAtomizedRules')
    @patch('bpgModel.getElements')
    @patch('bpgMaps.getTransformationPairs')
    @patch('bpgMaps.getNameDictionary')
    @patch('bpgMaps.getMaps')
    @patch('bpgMaps.makeFlow')
    @patch('os.path.isfile')
    def test_processActions_make_flow(self, mock_isfile, mock_makeFlow, mock_getMaps, mock_getNameDict, mock_getTransPairs, mock_getElements, mock_getRules):
        mock_isfile.return_value = True
        mock_getRules.return_value = ["rule1"]
        mock_getElements.return_value = (["patt1"], ["trans1"])
        mock_getTransPairs.return_value = (["tp1"], ["ir1"])
        mock_getNameDict.return_value = "names"
        mock_getMaps.return_value = "maps"

        input_str = "read_xml file.xml\nmake_pairs\nmake_maps\nmake_flow start A B end C"
        processActions(input_str)

        mock_makeFlow.assert_called_with("names", "maps", ["A", "B"], ["C"])

    @patch('bpgModel.getAtomizedRules')
    @patch('bpgModel.getElements')
    @patch('bpgMaps.getTransformationPairs')
    @patch('bpgMaps.getNameDictionary')
    @patch('bpgMaps.getMaps')
    @patch('bpgMaps.writeJSON')
    @patch('bpgAnnotate.Annotation')
    @patch('os.path.isfile')
    @patch('builtins.open', new_callable=mock_open, read_data="annotation data")
    def test_processActions_make_viz(self, mock_file, mock_isfile, mock_Annotation, mock_writeJSON, mock_getMaps, mock_getNameDict, mock_getTransPairs, mock_getElements, mock_getRules):
        mock_isfile.return_value = True
        mock_getRules.return_value = ["rule1"]
        mock_getElements.return_value = (["patt1"], ["trans1"])
        mock_getTransPairs.return_value = (["tp1"], ["ir1"])
        mock_getNameDict.return_value = "names"
        mock_getMaps.return_value = "maps"
        mock_writeJSON.return_value = "{}"

        # make_viz expects 'annot' to be defined, which happens in read_annot
        input_str = "read_xml file.xml\nmake_pairs\nmake_maps\nread_annot annot.txt\nmake_viz outfile"
        processActions(input_str)

        mock_writeJSON.assert_called()
        mock_file.assert_called_with("data.js", "w")

    @patch('bpgModel.getAtomizedRules')
    @patch('bpgModel.getElements')
    @patch('bpgMaps.getTransformationPairs')
    @patch('bpgMaps.getNameDictionary')
    @patch('bpgAnnotate.Annotation')
    @patch('os.path.isfile')
    @patch('builtins.open', new_callable=mock_open, read_data="annotation data")
    def test_processActions_read_annot(self, mock_file, mock_isfile, mock_Annotation, mock_getNameDict, mock_getTransPairs, mock_getElements, mock_getRules):
        mock_isfile.return_value = True
        mock_getRules.return_value = ["rule1"]
        mock_getElements.return_value = (["patt1"], ["trans1"])
        mock_getTransPairs.return_value = (["tp1"], ["ir1"])
        mock_getNameDict.return_value = "names"

        mock_annot_instance = MagicMock()
        mock_Annotation.return_value = mock_annot_instance

        input_str = "read_xml file.xml\nmake_pairs\nread_annot annot1.txt annot2.txt"
        processActions(input_str)

        self.assertEqual(mock_file.call_count, 2)
        mock_annot_instance.initialize.assert_called_with("names")
        mock_annot_instance.processAnnotations.assert_called_with("annotation dataannotation data", "names")

if __name__ == '__main__':
    unittest.main()
