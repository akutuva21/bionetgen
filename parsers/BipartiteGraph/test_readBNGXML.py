import sys
import unittest
from unittest.mock import MagicMock, patch

class TestFindBond(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Mock dependencies specifically for this module
        cls.module_patcher = patch.dict('sys.modules', {
            'lxml': MagicMock(),
            'lxml.etree': MagicMock(),
            'structures': MagicMock(),
            'parsers.BipartiteGraph.structures': MagicMock()
        })
        cls.module_patcher.start()

        # Add the directory to sys.path to resolve readBNGXML imports
        import os
        sys.path.insert(0, os.path.dirname(__file__))

    @classmethod
    def tearDownClass(cls):
        cls.module_patcher.stop()
        sys.path.pop(0)

    def setUp(self):
        # Import the function under test locally
        from readBNGXML import findBond
        self.findBond = findBond
    def test_findBond_match_site1(self):
        bond1 = MagicMock()
        bond1.get.side_effect = lambda k: 'comp1' if k == 'site1' else 'comp2'

        bond2 = MagicMock()
        bond2.get.side_effect = lambda k: 'comp3' if k == 'site1' else 'comp4'

        bondDefinitions = MagicMock()
        bondDefinitions.getchildren.return_value = [bond1, bond2]

        self.assertEqual(self.findBond(bondDefinitions, 'comp1'), '1')
        self.assertEqual(self.findBond(bondDefinitions, 'comp3'), '2')

    def test_findBond_match_site2(self):
        bond1 = MagicMock()
        bond1.get.side_effect = lambda k: 'comp1' if k == 'site1' else 'comp2'

        bond2 = MagicMock()
        bond2.get.side_effect = lambda k: 'comp3' if k == 'site1' else 'comp4'

        bondDefinitions = MagicMock()
        bondDefinitions.getchildren.return_value = [bond1, bond2]

        self.assertEqual(self.findBond(bondDefinitions, 'comp2'), '1')
        self.assertEqual(self.findBond(bondDefinitions, 'comp4'), '2')

    def test_findBond_no_match(self):
        bond1 = MagicMock()
        bond1.get.side_effect = lambda k: 'comp1' if k == 'site1' else 'comp2'

        bondDefinitions = MagicMock()
        bondDefinitions.getchildren.return_value = [bond1]

        self.assertIsNone(self.findBond(bondDefinitions, 'comp3'))

    def test_empty_bonds(self):
        bondDefinitions = MagicMock()
        bondDefinitions.getchildren.return_value = []

        self.assertIsNone(self.findBond(bondDefinitions, 'comp1'))

if __name__ == '__main__':
    unittest.main()
