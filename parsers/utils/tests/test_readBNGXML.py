import unittest
from unittest.mock import MagicMock
import sys
import os

# Mock dependencies
sys.modules['lxml'] = MagicMock()
sys.modules['lxml.etree'] = MagicMock()
sys.modules['pygraphviz'] = MagicMock()
sys.modules['pyparsing'] = MagicMock()
sys.modules['networkx'] = MagicMock()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import readBNGXML

class TestReadBNGXML(unittest.TestCase):

    def test_createSpecies_valid(self):
        pattern = MagicMock()
        pattern.get.return_value = '1'

        mol_element = MagicMock()
        molecule = MagicMock()
        molecule.get.side_effect = lambda key: 'M1' if key == 'name' else 'id1' if key == 'id' else None
        molecule.find.return_value = None
        mol_element.getchildren.return_value = [molecule]

        bonds_element = MagicMock()
        bond1 = MagicMock()
        bond1.get.side_effect = lambda key: 'site1' if key == 'site1' else 'site2' if key == 'site2' else None

        # We need to make sure bonds_element works in a for loop and boolean context
        bonds_element.__iter__.return_value = [bond1]
        bonds_element.__bool__.return_value = True

        def mock_find(xpath):
            if 'ListOfMolecules' in xpath:
                return mol_element
            if 'ListOfBonds' in xpath:
                return bonds_element
            return None

        pattern.find.side_effect = mock_find

        species, tmpDict = readBNGXML.createSpecies(pattern)

        self.assertEqual(species.idx, '1')
        self.assertEqual(len(species.molecules), 1)
        self.assertEqual(species.bonds, [('site1', 'site2')])
        self.assertIn('id1', tmpDict)

    def test_createSpecies_no_molecules_no_bonds(self):
        pattern = MagicMock()
        pattern.get.return_value = '2'

        mol_element = MagicMock()
        mol_element.getchildren.return_value = []

        def mock_find(xpath):
            if 'ListOfMolecules' in xpath:
                return mol_element
            if 'ListOfBonds' in xpath:
                return None
            return None

        pattern.find.side_effect = mock_find

        species, tmpDict = readBNGXML.createSpecies(pattern)

        self.assertEqual(species.idx, '2')
        self.assertEqual(len(species.molecules), 0)
        self.assertEqual(species.bonds, [])
        self.assertEqual(tmpDict, {})

if __name__ == '__main__':
    unittest.main()
