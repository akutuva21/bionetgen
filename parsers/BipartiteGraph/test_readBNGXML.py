import sys
import unittest
from unittest.mock import MagicMock

# Try to mock lxml if it's missing
try:
    import lxml.etree
except ImportError:
    import sys
    sys.modules['lxml'] = MagicMock()
    sys.modules['lxml.etree'] = MagicMock()

# Try to mock pyparsing if it's missing, required by smallStructures.py
try:
    import pyparsing
except ImportError:
    mock_pyparsing = MagicMock()
    mock_pyparsing.Word = MagicMock()
    mock_pyparsing.Suppress = MagicMock()
    mock_pyparsing.Group = MagicMock()
    mock_pyparsing.Optional = MagicMock()
    mock_pyparsing.ZeroOrMore = MagicMock()
    mock_pyparsing.OneOrMore = MagicMock()
    mock_pyparsing.alphanums = ""
    mock_pyparsing.alphas = ""
    mock_pyparsing.nums = ""
    mock_pyparsing.printables = ""
    mock_pyparsing.Combine = MagicMock()
    mock_pyparsing.Literal = MagicMock()
    mock_pyparsing.Keyword = MagicMock()
    mock_pyparsing.Forward = MagicMock()
    mock_pyparsing.Dict = MagicMock()
    mock_pyparsing.ParseException = Exception
    sys.modules['pyparsing'] = mock_pyparsing

import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../utils/'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers.BipartiteGraph.readBNGXML import parseMolecules

class TestParseMolecules(unittest.TestCase):
    def test_parseMolecules_no_components(self):
        # Scenario A: Molecule without components
        mock_molecule = MagicMock()
        mock_molecule.get.side_effect = lambda key: 'mol1' if key == 'name' else 'id1'
        mock_molecule.find.return_value = None

        mol = parseMolecules(mock_molecule)

        self.assertEqual(mol.name, 'mol1')
        # Depending on structures.Molecule, let's assume it has components list/dict
        self.assertEqual(len(mol.components), 0)

    def test_parseMolecules_with_components(self):
        # Scenario B: Molecule with components
        mock_molecule = MagicMock()
        mock_molecule.get.side_effect = lambda key: 'mol2' if key == 'name' else 'id2'

        mock_components = MagicMock()

        mock_comp1 = MagicMock()
        mock_comp1.get.side_effect = lambda key: 'comp1' if key == 'name' else 'cid1'

        mock_comp2 = MagicMock()
        mock_comp2.get.side_effect = lambda key: 'comp2' if key == 'name' else 'cid2'

        mock_components.getchildren.return_value = [mock_comp1, mock_comp2]

        mock_molecule.find.return_value = mock_components

        mol = parseMolecules(mock_molecule)

        self.assertEqual(mol.name, 'mol2')
        self.assertEqual(len(mol.components), 2)

        # Check components
        # smallStructures.Molecule stores components in self.components
        comp_names = [c.name for c in mol.components]
        self.assertIn('comp1', comp_names)
        self.assertIn('comp2', comp_names)

if __name__ == '__main__':
    unittest.main()
