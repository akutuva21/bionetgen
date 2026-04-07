import unittest
from unittest.mock import patch, MagicMock
import sys

class TestCollapsedContactMap(unittest.TestCase):
    def setUp(self):
        # We need to setup the mocks in sys.modules *before* we import the target module
        self.patcher = patch.dict('sys.modules', {'networkx': MagicMock(), 'readBNGXML': MagicMock()})
        self.patcher.start()

        # Now we can import the module
        import parsers.ContactMap.collapsedContactMap as collapsedContactMap
        self.collapsedContactMap = collapsedContactMap
        self.mock_nx = sys.modules['networkx']
        self.mock_nx.reset_mock()

    def tearDown(self):
        # Clean up the patcher
        self.patcher.stop()

        # Ensure we don't leave the module cached so other tests are isolated
        if 'parsers.ContactMap.collapsedContactMap' in sys.modules:
            del sys.modules['parsers.ContactMap.collapsedContactMap']

    @patch('parsers.ContactMap.collapsedContactMap.extractSingleTransformation')
    def test_createCollapsedContact(self, mock_extract):
        # Setup mock return values for extractSingleTransformation
        # atomicArray, transformationCenter, transformationContext, productElements, actionName, label

        # Mock rules
        mock_rule = MagicMock()
        mock_action_addbond = MagicMock()
        mock_action_addbond.action = 'AddBond'

        mock_action_statechange = MagicMock()
        mock_action_statechange.action = 'StateChange'

        mock_action_add = MagicMock()
        mock_action_add.action = 'Add'

        mock_rule.actions = [mock_action_addbond, mock_action_statechange, mock_action_add]

        mock_reactant_molecule = MagicMock()
        mock_reactant_molecule.name = 'A'
        mock_reactant = MagicMock()
        mock_reactant.molecules = [mock_reactant_molecule]
        mock_reactant_molecule2 = MagicMock()
        mock_reactant_molecule2.name = 'R'
        mock_reactant2 = MagicMock()
        mock_reactant2.molecules = [mock_reactant_molecule2]
        mock_rule.reactants = [mock_reactant, mock_reactant2]

        mock_product_molecule = MagicMock()
        mock_product_molecule.name = 'C'

        mock_product_molecule2 = MagicMock()
        mock_product_molecule2.name = 'P'

        mock_product = MagicMock()
        mock_product.molecules = [mock_product_molecule, mock_product_molecule2]
        mock_rule.products = [mock_product]

        rules = [(mock_rule, None, None, None)]

        # Mock species
        mock_species_unit = MagicMock()
        mock_species_unit.name = 'A'
        species = [mock_species_unit]

        # We need to adapt the transformationCenter for the different actions
        # For AddBond (idx 0), we need two bond partners or one
        # For StateChange (idx 1), we need molecule~state
        # For Add (idx 2), we don't strictly need a specific transformationCenter format in the loop body
        mock_extract.return_value = (
            {},
            [['A(b)', 'B(a)'], ['C(s~P)'], []],
            [[], [], []],
            [[], [], []],
            [],
            []
        )

        mock_graph = MagicMock()
        # Ensure node checks like `if element not in graph.node:` work
        mock_graph.node = {}
        self.mock_nx.DiGraph.return_value = mock_graph

        # Call the function
        self.collapsedContactMap.createCollapsedContact(rules, species, [1], 'test_output')

        # Verify networkx DiGraph was created
        self.mock_nx.DiGraph.assert_called_once()

        # Verify nodes and edges were added
        # initial species node
        mock_graph.add_node.assert_any_call('A', graphics={'type': 'roundrectangle', 'fill': '#FFCC00'})

        # AddBond edge (A, B)
        mock_graph.add_edge.assert_any_call('A', 'B', graphics={'fill': '#000000'})

        # StateChange node and edge
        # The node name will be molecule + '_' + state
        # Our mock transformationCenter is 'C(s~P)'
        # `molecule = [x.split('(')[0] for x in transformationCenter[idx]]` -> ['C']
        # `state = [x.split('(')[1].split('~')[0] for x in transformationCenter[idx]]` -> ['s']
        # Wait, the state string parsing splits by `~`. So 'C(s~P)' splits to 's', not 'P'.
        # So it becomes 'C_s'.
        mock_graph.add_node.assert_any_call('C_s', graphics={'type': 'circle', 'fill': '#CCFFCC'})
        mock_graph.add_edge.assert_any_call('C_s', 'C', graphics={'fill': '#000000'})

        # Add (nonatomicset) node and edges
        mock_graph.add_node.assert_any_call(1, graphics={'type': 'hexagon'})
        # Verify connection from reactant to mainidx and mainidx to product
        # 'A' and 'B' are in transformationCenter[0]
        # 'C' is in transformationCenter[1]
        # So 'R' and 'P' will remain in activeReactants/activeProducts.
        mock_graph.add_edge.assert_any_call('R', 1, graphics={'targetArrow': 'standard'})
        mock_graph.add_edge.assert_any_call(1, 'P')

        # Verify write_gml was called with the correct filename
        self.mock_nx.write_gml.assert_called_once_with(mock_graph, 'test_output.gml')

if __name__ == '__main__':
    unittest.main()