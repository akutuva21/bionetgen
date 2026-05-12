import unittest
import pexpect
import subprocess
try:
    from unittest.mock import patch, MagicMock, call
except ImportError:
    from mock import patch, MagicMock, call

import parsers.utils.consoleCommands as consoleCommands

class TestConsoleCommands(unittest.TestCase):

    @patch('subprocess.call')
    @patch('pexpect.spawn')
    def test_bngl2sbml_success(self, mock_spawn, mock_call):
        # Setup mock to not raise an exception
        mock_bngconsole = MagicMock()
        mock_spawn.return_value = mock_bngconsole

        # Call the function
        consoleCommands.bngl2sbml('dummy.bngl', timeout=42)

        # Verify pexpect.spawn was called correctly
        mock_spawn.assert_called_once_with('{0} --console'.format(consoleCommands.getBngExecutable()), timeout=42)

        # Verify the sequence of calls
        expected_calls = [
            call.expect('BNG>'),
            call.sendline('load dummy.bngl'),
            call.expect('BNG>'),
            call.sendline('action generate_network()'),
            call.expect('BNG>'),
            call.sendline('action writeSBML()'),
            call.expect('BNG>'),
            call.close()
        ]
        mock_bngconsole.assert_has_calls(expected_calls, any_order=False)

        # Verify subprocess.call was NOT called
        mock_call.assert_not_called()

    @patch('subprocess.call')
    @patch('pexpect.spawn')
    def test_bngl2sbml_timeout(self, mock_spawn, mock_call):
        # Setup mock to raise TIMEOUT
        mock_spawn.side_effect = pexpect.TIMEOUT('Timeout')

        # Call the function
        consoleCommands.bngl2sbml('dummy.bngl')

        # Verify subprocess.call was called with the right arguments to kill bngdev
        mock_call.assert_called_once_with(['/usr/bin/killall', 'bngdev'], shell=False)

if __name__ == '__main__':
    unittest.main()
