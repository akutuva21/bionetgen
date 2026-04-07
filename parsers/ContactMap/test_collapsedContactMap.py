import unittest
from unittest.mock import MagicMock, call
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from collapsedContactMap import extractSingleTransformation, solveWildcards

class TestCollapsedContactMap(unittest.TestCase):

    def test_solveWildcards_basic(self):
        # Setup mock molecular components
        mol1 = MagicMock()
        mol1.name = "Mol1"

        mol2 = MagicMock()
        mol2.name = "Mol2"

        atomic1 = MagicMock()
        atomic1.molecules = [mol1, mol2]

        atomic_wildcard = MagicMock()
        atomic_wildcard.molecules = [mol1]

        # This will simulate atomicArray passed into solveWildcards
        atomicArray = {
            "A+": atomic_wildcard,
            "B": atomic1
        }

        solveWildcards(atomicArray)

        # After solveWildcards, standinArray is merged. Since "A+" has a wildcard '+', and its first molecule name "Mol1"
        # is in the molecule names of "B", it should append "B" into the list of "A+".

        # Notice in the original implementation `standinArray[wildcard] = []` and it appends values.
        # atomicArray.update(standinArray) will overwrite the wildcard key with a list.

        self.assertIsInstance(atomicArray["A+"], list)
        self.assertEqual(len(atomicArray["A+"]), 1)
        self.assertEqual(atomicArray["A+"][0], atomic1)

    def test_solveWildcards_no_wildcard(self):
        # Setup mock molecular components
        mol1 = MagicMock()
        mol1.name = "Mol1"

        atomic1 = MagicMock()
        atomic1.molecules = [mol1, mol1]

        atomicArray = {
            "B": atomic1
        }

        solveWildcards(atomicArray)

        # Should not be modified
        self.assertEqual(atomicArray["B"], atomic1)

    def test_solveWildcards_multiple_matches(self):
        mol1 = MagicMock()
        mol1.name = "Mol1"
        mol2 = MagicMock()
        mol2.name = "Mol2"
        mol3 = MagicMock()
        mol3.name = "Mol3"

        atomic1 = MagicMock()
        atomic1.molecules = [mol1, mol2]

        atomic2 = MagicMock()
        atomic2.molecules = [mol1, mol3]

        atomic_wildcard = MagicMock()
        atomic_wildcard.molecules = [mol1]

        atomicArray = {
            "A+": atomic_wildcard,
            "B": atomic1,
            "C": atomic2
        }

        solveWildcards(atomicArray)

        self.assertIsInstance(atomicArray["A+"], list)
        self.assertEqual(len(atomicArray["A+"]), 2)
        self.assertIn(atomic1, atomicArray["A+"])
        self.assertIn(atomic2, atomicArray["A+"])

    def test_extractSingleTransformation_basic(self):
        rule = MagicMock()

        # Mock actions
        action = MagicMock()
        action.action = "AddBond"
        action.site1 = "site_A"
        action.site2 = "site_B"
        rule.actions = [action]

        # Mock reactants
        reactant = MagicMock()
        reactant.__str__.return_value = "Reactant1"
        reactant.extractAtomicPatterns.return_value = (
            {"pattern1": MagicMock()},
            ["center1"],
            ["context1"]
        )
        rule.reactants = [reactant]

        # Mock products
        product = MagicMock()
        product.__str__.return_value = "Product1"
        product.extractAtomicPatterns.return_value = (
            {"pattern2": MagicMock()},
            ["center2"],
            ["context2"]
        )
        rule.products = [product]

        # Mock mapping
        rule.mapping = [("site_A", "site_A_prod"), ("site_B", "site_B_prod")]

        atomicArray, transformationCenter, transformationContext, productElements, actionName, label = extractSingleTransformation(rule)

        self.assertEqual(len(transformationCenter), 1)
        self.assertEqual(transformationCenter[0], {"center1"})
        self.assertEqual(len(transformationContext), 1)
        self.assertEqual(transformationContext[0], {"context1"})

        self.assertEqual(len(productElements), 1)
        self.assertEqual(productElements[0], {"center2"})

        self.assertEqual(actionName, ["1-AddBond"])
        self.assertEqual(label, ["Reactant1->Product1->1-AddBond"])

    def test_extractSingleTransformation_multiple_actions(self):
        rule = MagicMock()

        action1 = MagicMock()
        action1.action = "StateChange"
        action1.site1 = "site_A"
        action1.site2 = None

        action2 = MagicMock()
        action2.action = "AddBond"
        action2.site1 = "site_C"
        action2.site2 = "site_D"

        rule.actions = [action1, action2]

        reactant = MagicMock()
        reactant.__str__.return_value = "R1"
        reactant.extractAtomicPatterns.return_value = (
            {"pattern_R": MagicMock()},
            ["center_R"],
            ["context_R"]
        )
        rule.reactants = [reactant]

        product = MagicMock()
        product.__str__.return_value = "P1"
        product.extractAtomicPatterns.return_value = (
            {"pattern_P": MagicMock()},
            ["center_P"],
            ["context_P"]
        )
        rule.products = [product]

        rule.mapping = [("site_A", "site_A_prod"), ("site_C", "site_C_prod"), ("site_D", "site_D_prod")]

        atomicArray, transformationCenter, transformationContext, productElements, actionName, label = extractSingleTransformation(rule)

        self.assertEqual(len(transformationCenter), 2)
        self.assertEqual(len(transformationContext), 2)
        self.assertEqual(len(productElements), 2)

        self.assertEqual(actionName, ["1-StateChange", "1-AddBond"])
        self.assertEqual(label, ["R1->P1->1-StateChange", "R1->P1->1-AddBond"])

if __name__ == "__main__":
    unittest.main()
