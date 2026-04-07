import unittest
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../utils')))

# Mock external dependencies missing in the environment
sys.modules['lxml'] = MagicMock()
sys.modules['lxml.etree'] = MagicMock()
sys.modules['networkx'] = MagicMock()
sys.modules['pygraphviz'] = MagicMock()

# Mock pyparsing since it's also missing in typical bare envs
mock_pyparsing = MagicMock()
mock_pyparsing.Word = MagicMock(return_value=MagicMock())
mock_pyparsing.Suppress = MagicMock(return_value=MagicMock())
mock_pyparsing.Group = MagicMock(return_value=MagicMock())
mock_pyparsing.Optional = MagicMock(return_value=MagicMock())
mock_pyparsing.ZeroOrMore = MagicMock(return_value=MagicMock())
mock_pyparsing.alphanums = 'alphanums'
mock_pyparsing.alphas = 'alphas'
sys.modules['pyparsing'] = mock_pyparsing

from collapsedContactMap import extractSingleTransformation, solveWildcards, extractMolecules, getMapping

class TestCollapsedContactMap(unittest.TestCase):
    @patch('collapsedContactMap.extractMolecules')
    @patch('collapsedContactMap.solveWildcards')
    def test_extractSingleTransformation(self, mock_solveWildcards, mock_extractMolecules):
        # Setup mocks
        mock_extractMolecules.side_effect = [
            ({'atomic1': 'data1'}, set(['rc1']), set(['ctx1'])), # First action, react
            ({'atomic2': 'data2'}, set(['rc2']), set(['ctx2'])), # First action, product
        ]

        # Setup rule mock
        rule = MagicMock()

        action = MagicMock()
        action.action = 'AddBond'
        action.site1 = 'siteA'
        action.site2 = 'siteB'
        rule.actions = [action]

        reactant = MagicMock()
        reactant.__str__.return_value = 'ReactantA'
        rule.reactants = [reactant]

        product = MagicMock()
        product.__str__.return_value = 'ProductA'
        rule.products = [product]

        rule.mapping = [['siteA', 'siteA_prod'], ['siteB', 'siteB_prod']]

        # Call the function
        result = extractSingleTransformation(rule)

        # Check result
        atomicArray, transformationCenter, transformationContext, productElements, actionName, label = result

        self.assertEqual(atomicArray, {'atomic1': 'data1', 'atomic2': 'data2'})
        self.assertEqual(transformationCenter, [set(['rc1'])])
        self.assertEqual(transformationContext, [set(['ctx1'])])
        self.assertEqual(productElements, [set(['rc2'])])
        self.assertEqual(actionName, ['1-AddBond'])
        self.assertEqual(label, ['ReactantA->ProductA->1-AddBond'])

        mock_solveWildcards.assert_called_once_with({'atomic1': 'data1', 'atomic2': 'data2'})
        mock_extractMolecules.assert_any_call('AddBond', 'siteA', 'siteB', rule.reactants)
        mock_extractMolecules.assert_any_call('AddBond', 'siteA_prod', 'siteB_prod', rule.products)

    @patch('collapsedContactMap.extractMolecules')
    @patch('collapsedContactMap.solveWildcards')
    def test_extractSingleTransformation_multiple_actions(self, mock_solveWildcards, mock_extractMolecules):
        # Setup mocks
        mock_extractMolecules.side_effect = [
            ({'atomic1': 'data1'}, set(['rc1']), set(['ctx1'])), # First action, react
            ({'atomic2': 'data2'}, set(['rc2']), set(['ctx2'])), # First action, product
            ({'atomic3': 'data3'}, set(['rc3']), set(['ctx3'])), # Second action, react
            ({'atomic4': 'data4'}, set(['rc4']), set(['ctx4'])), # Second action, product
        ]

        # Setup rule mock
        rule = MagicMock()

        action1 = MagicMock()
        action1.action = 'AddBond'
        action1.site1 = 'siteA'
        action1.site2 = 'siteB'

        action2 = MagicMock()
        action2.action = 'StateChange'
        action2.site1 = 'siteC'
        action2.site2 = 'siteD'

        rule.actions = [action1, action2]

        reactant = MagicMock()
        reactant.__str__.return_value = 'ReactantA'
        rule.reactants = [reactant]

        product = MagicMock()
        product.__str__.return_value = 'ProductA'
        rule.products = [product]

        rule.mapping = [['siteA', 'siteA_prod'], ['siteB', 'siteB_prod'], ['siteC', 'siteC_prod'], ['siteD', 'siteD_prod']]

        # Call the function
        result = extractSingleTransformation(rule)

        # Check result
        atomicArray, transformationCenter, transformationContext, productElements, actionName, label = result

        self.assertEqual(atomicArray, {'atomic1': 'data1', 'atomic2': 'data2', 'atomic3': 'data3', 'atomic4': 'data4'})
        self.assertEqual(transformationCenter, [set(['rc1']), set(['rc3'])])
        self.assertEqual(transformationContext, [set(['ctx1']), set(['ctx3'])])
        self.assertEqual(productElements, [set(['rc2']), set(['rc4'])])

        # The code in extractSingleTransformation increments index BEFORE the loop,
        # but NOT INSIDE the loop. This means all actions get the same index.
        # So we should expect '1-AddBond' and '1-StateChange'.
        self.assertEqual(actionName, ['1-AddBond', '1-StateChange'])
        self.assertEqual(label, ['ReactantA->ProductA->1-AddBond', 'ReactantA->ProductA->1-StateChange'])

        mock_solveWildcards.assert_called_once_with({'atomic1': 'data1', 'atomic2': 'data2', 'atomic3': 'data3', 'atomic4': 'data4'})

if __name__ == '__main__':
    unittest.main()
