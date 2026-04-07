import unittest
from unittest.mock import MagicMock
import sys
import os

# Add the directory containing readBNGXML.py to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now we can import readBNGXML with mocked dependencies
from unittest.mock import patch

with patch.dict('sys.modules', {'lxml': MagicMock(), 'lxml.etree': MagicMock()}):
    import readBNGXML

class TestReadBNGXML(unittest.TestCase):
    def test_findBond_match_site1(self):
        # Setup
        bond_mock = MagicMock()
        bond_mock.get.side_effect = lambda key: 'comp1' if key == 'site1' else 'comp2'

        bondDefinitions = MagicMock()
        bondDefinitions.getchildren.return_value = [bond_mock]

        # Execute
        result = readBNGXML.findBond(bondDefinitions, 'comp1')

        # Verify
        self.assertEqual(result, '1')

    def test_findBond_match_site2(self):
        # Setup
        bond_mock = MagicMock()
        bond_mock.get.side_effect = lambda key: 'comp1' if key == 'site1' else 'comp2'

        bondDefinitions = MagicMock()
        bondDefinitions.getchildren.return_value = [bond_mock]

        # Execute
        result = readBNGXML.findBond(bondDefinitions, 'comp2')

        # Verify
        self.assertEqual(result, '1')

    def test_findBond_multiple_bonds(self):
        # Setup
        bond1 = MagicMock()
        bond1.get.side_effect = lambda key: 'comp1' if key == 'site1' else 'comp2'

        bond2 = MagicMock()
        bond2.get.side_effect = lambda key: 'comp3' if key == 'site1' else 'comp4'

        bondDefinitions = MagicMock()
        bondDefinitions.getchildren.return_value = [bond1, bond2]

        # Execute
        result = readBNGXML.findBond(bondDefinitions, 'comp4')

        # Verify
        self.assertEqual(result, '2')

    def test_findBond_no_match(self):
        # Setup
        bond_mock = MagicMock()
        bond_mock.get.side_effect = lambda key: 'comp1' if key == 'site1' else 'comp2'

        bondDefinitions = MagicMock()
        bondDefinitions.getchildren.return_value = [bond_mock]

        # Execute
        result = readBNGXML.findBond(bondDefinitions, 'comp3')

        # Verify
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
