import sys
import os
import unittest
from unittest.mock import MagicMock

# Add the current directory to sys.path so we import the correct readBNGXML
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock lxml and structures before importing readBNGXML
sys.modules['lxml'] = MagicMock()
sys.modules['lxml.etree'] = MagicMock()

# also mock structures
sys.modules['structures'] = MagicMock()

import readBNGXML

class MockElement:
    def __init__(self, attrs):
        self.attrs = attrs

    def get(self, key):
        return self.attrs.get(key)

class MockParent:
    def __init__(self, children):
        self.children = children

    def getchildren(self):
        return self.children

class TestReadBNGXML(unittest.TestCase):
    def test_findBond(self):
        bond1 = MockElement({'site1': 'comp1', 'site2': 'comp2'})
        bond2 = MockElement({'site1': 'comp3', 'site2': 'comp4'})
        bond3 = MockElement({'site1': 'comp5', 'site2': 'comp6'})

        bondDefinitions = MockParent([bond1, bond2, bond3])

        # Test finding component as site1
        self.assertEqual(readBNGXML.findBond(bondDefinitions, "comp1"), "1")
        self.assertEqual(readBNGXML.findBond(bondDefinitions, "comp3"), "2")
        self.assertEqual(readBNGXML.findBond(bondDefinitions, "comp5"), "3")

        # Test finding component as site2
        self.assertEqual(readBNGXML.findBond(bondDefinitions, "comp2"), "1")
        self.assertEqual(readBNGXML.findBond(bondDefinitions, "comp4"), "2")
        self.assertEqual(readBNGXML.findBond(bondDefinitions, "comp6"), "3")

        # Test component not found
        self.assertIsNone(readBNGXML.findBond(bondDefinitions, "comp7"))

        # Test empty bondDefinitions
        emptyDefinitions = MockParent([])
        self.assertIsNone(readBNGXML.findBond(emptyDefinitions, "comp1"))

if __name__ == '__main__':
    unittest.main()
