import unittest
from lxml import etree
import structures as st
import readBNGXML

class TestReadBNGXML(unittest.TestCase):
    def test_parseMolecules_no_components(self):
        xml_str = '<MoleculeType id="m1" name="Mol1"></MoleculeType>'
        element = etree.fromstring(xml_str)
        mol = readBNGXML.parseMolecules(element)
        self.assertEqual(mol.name, "Mol1")
        self.assertEqual(mol.idx, "m1")
        self.assertEqual(len(mol.components), 0)

    def test_parseMolecules_with_components(self):
        xml_str = '''
        <MoleculeType id="m2" name="Mol2">
            <sbml:ListOfComponentTypes xmlns:sbml="http://www.sbml.org/sbml/level3">
                <sbml:ComponentType id="c1" name="Comp1"/>
                <sbml:ComponentType id="c2" name="Comp2"/>
            </sbml:ListOfComponentTypes>
        </MoleculeType>
        '''
        element = etree.fromstring(xml_str)
        mol = readBNGXML.parseMolecules(element)
        self.assertEqual(mol.name, "Mol2")
        self.assertEqual(mol.idx, "m2")
        self.assertEqual(len(mol.components), 2)
        self.assertEqual(mol.components[0].name, "Comp1")
        self.assertEqual(mol.components[0].idx, "c1")
        self.assertEqual(mol.components[1].name, "Comp2")
        self.assertEqual(mol.components[1].idx, "c2")

if __name__ == '__main__':
    unittest.main()
