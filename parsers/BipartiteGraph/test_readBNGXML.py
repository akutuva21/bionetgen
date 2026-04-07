import unittest
import sys
import os
from unittest.mock import MagicMock

# Allow imports from the same directory without lxml available
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock lxml so we don't need it installed to load the module
sys.modules['lxml'] = MagicMock()
sys.modules['lxml.etree'] = MagicMock()

from xml.etree import ElementTree as etree

import readBNGXML as rbng

class TestReadBNGXML(unittest.TestCase):

    def test_findBond(self):
        # Create mock elements for bonds
        bonds_str = '''
        <ListOfBonds xmlns="http://www.sbml.org/sbml/level3">
            <Bond site1="c1" site2="c2" />
            <Bond site1="c3" site2="c4" />
        </ListOfBonds>
        '''
        bonds = etree.fromstring(bonds_str)

        self.assertEqual(rbng.findBond(bonds, 'c1'), '1')
        self.assertEqual(rbng.findBond(bonds, 'c2'), '1')
        self.assertEqual(rbng.findBond(bonds, 'c3'), '2')
        self.assertEqual(rbng.findBond(bonds, 'c4'), '2')
        self.assertIsNone(rbng.findBond(bonds, 'c5'))

    def test_createMolecule(self):
        mol_str = '''
        <Molecule name="A" id="m1" xmlns="http://www.sbml.org/sbml/level3">
            <ListOfComponents>
                <Component name="x" id="c1" numberOfBonds="+" state="P" />
                <Component name="y" id="c2" numberOfBonds="0" state="U" />
                <Component name="z" id="c3" numberOfBonds="1" />
            </ListOfComponents>
        </Molecule>
        '''
        bonds_str = '''
        <ListOfBonds xmlns="http://www.sbml.org/sbml/level3">
            <Bond site1="c3" site2="c4" />
        </ListOfBonds>
        '''
        molecule_elem = etree.fromstring(mol_str)
        bonds_elem = etree.fromstring(bonds_str)

        mol, nameDict = rbng.createMolecule(molecule_elem, bonds_elem)

        self.assertEqual(mol.name, 'A')
        self.assertEqual(mol.idx, 'm1')
        self.assertEqual(nameDict['m1'], 'A')
        self.assertEqual(nameDict['c1'], 'x')
        self.assertEqual(nameDict['c2'], 'y')
        self.assertEqual(nameDict['c3'], 'z')

        c1 = mol.getComponent('x')
        self.assertEqual(c1.idx, 'c1')
        self.assertIn('+', c1.bonds)
        self.assertEqual(c1.activeState, 'P')

        c2 = mol.getComponent('y')
        self.assertEqual(c2.idx, 'c2')
        self.assertEqual(len(c2.bonds), 0)
        self.assertEqual(c2.activeState, 'U')

        c3 = mol.getComponent('z')
        self.assertEqual(c3.idx, 'c3')
        self.assertIn('1', c3.bonds)
        self.assertEqual(c3.activeState, '')

    def test_createSpecies(self):
        pattern_str = '''
        <ReactantPattern id="p1" xmlns="http://www.sbml.org/sbml/level3">
            <ListOfMolecules>
                <Molecule name="A" id="m1">
                    <ListOfComponents>
                        <Component name="x" id="c1" numberOfBonds="1" />
                    </ListOfComponents>
                </Molecule>
                <Molecule name="B" id="m2">
                    <ListOfComponents>
                        <Component name="y" id="c2" numberOfBonds="1" />
                    </ListOfComponents>
                </Molecule>
            </ListOfMolecules>
            <ListOfBonds>
                <Bond site1="c1" site2="c2" />
            </ListOfBonds>
        </ReactantPattern>
        '''
        pattern = etree.fromstring(pattern_str)

        species, tmpDict = rbng.createSpecies(pattern)

        self.assertEqual(species.idx, 'p1')
        self.assertEqual(len(species.molecules), 2)
        self.assertEqual(species.molecules[0].name, 'A')
        self.assertEqual(species.molecules[1].name, 'B')
        self.assertEqual(len(species.bonds), 1)
        self.assertEqual(species.bonds[0], ('c1', 'c2'))
        self.assertEqual(tmpDict['m1'], 'A')
        self.assertEqual(tmpDict['m2'], 'B')
        self.assertEqual(tmpDict['c1'], 'x')
        self.assertEqual(tmpDict['c2'], 'y')

    def test_parseRule(self):
        rule_str = '''
        <ReactionRule xmlns="http://www.sbml.org/sbml/level3">
            <ListOfReactantPatterns>
                <ReactantPattern id="rp1">
                    <ListOfMolecules>
                        <Molecule name="A" id="rm1">
                            <ListOfComponents>
                                <Component name="x" id="rc1" numberOfBonds="0" />
                            </ListOfComponents>
                        </Molecule>
                    </ListOfMolecules>
                </ReactantPattern>
            </ListOfReactantPatterns>
            <ListOfProductPatterns>
                <ProductPattern id="pp1">
                    <ListOfMolecules>
                        <Molecule name="A" id="pm1">
                            <ListOfComponents>
                                <Component name="x" id="pc1" numberOfBonds="0" state="P" />
                            </ListOfComponents>
                        </Molecule>
                    </ListOfMolecules>
                </ProductPattern>
            </ListOfProductPatterns>
            <ListOfOperations>
                <StateChange id="op1" site="pc1" />
                <Add id="op2" />
                <AddBond site1="pc1" site2="pc2" />
            </ListOfOperations>
            <Map>
                <MapItem sourceID="rc1" targetID="pc1" />
            </Map>
        </ReactionRule>
        '''
        rule = etree.fromstring(rule_str)

        reactants, products, actions, mappings, nameDict = rbng.parseRule(rule)

        self.assertEqual(len(reactants), 1)
        self.assertEqual(reactants[0].idx, 'rp1')
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].idx, 'pp1')

        self.assertEqual(len(actions), 3)
        self.assertEqual(actions[0].action, 'StateChange')
        self.assertEqual(actions[0].site1, 'pc1')
        self.assertEqual(actions[1].action, 'Add')
        self.assertEqual(actions[1].site1, 'op2')
        self.assertEqual(actions[2].action, 'AddBond')
        self.assertEqual(actions[2].site1, 'pc1')
        self.assertEqual(actions[2].site2, 'pc2')

        self.assertEqual(len(mappings), 1)
        self.assertEqual(mappings[0], ('rc1', 'pc1'))

        self.assertEqual(nameDict['rm1'], 'A')
        self.assertEqual(nameDict['pm1'], 'A')

    def test_parseMolecules(self):
        mol_str = '''
        <MoleculeType name="A" id="mt1" xmlns="http://www.sbml.org/sbml/level3">
            <ListOfComponentTypes>
                <ComponentType name="x" id="ct1" />
                <ComponentType name="y" id="ct2" />
            </ListOfComponentTypes>
        </MoleculeType>
        '''
        mol_elem = etree.fromstring(mol_str)

        mol = rbng.parseMolecules(mol_elem)

        self.assertEqual(mol.name, 'A')
        self.assertEqual(mol.idx, 'mt1')
        self.assertEqual(len(mol.components), 2)
        self.assertEqual(mol.components[0].name, 'x')
        self.assertEqual(mol.components[0].idx, 'ct1')
        self.assertEqual(mol.components[1].name, 'y')
        self.assertEqual(mol.components[1].idx, 'ct2')

if __name__ == '__main__':
    unittest.main()
