"""kytos.cli.commands.users.parser tests."""
import sys
import unittest
from unittest.mock import patch

from kytos.cli.commands.users.parser import call, parse
from kytos.utils.exceptions import KytosException


class TestUsersParser(unittest.TestCase):
    """Test the UsersAPI parser methods."""

    @staticmethod
    @patch('kytos.cli.commands.users.parser.call')
    @patch('kytos.cli.commands.users.parser.docopt', return_value='args')
    def test_parse(*args):
        """Test parse method."""
        (_, mock_call) = args
        with patch.object(sys, 'argv', ['A', 'B', 'C']):
            parse('argv')

            mock_call.assert_called_with('C', 'args')

    @staticmethod
    @patch('sys.exit')
    @patch('kytos.cli.commands.users.parser.call')
    @patch('kytos.cli.commands.users.parser.docopt', return_value='args')
    def test_parse__error(*args):
        """Test parse method to error case."""
        (_, mock_call, mock_exit) = args
        mock_call.side_effect = KytosException
        with patch.object(sys, 'argv', ['A', 'B', 'C']):
            parse('argv')

            mock_exit.assert_called()

    @staticmethod
    @patch('kytos.cli.commands.users.api.UsersAPI.register')
    @patch('kytos.utils.config.KytosConfig')
    def test_call(*args):
        """Test call method."""
        (_, mock_users_api) = args
        call('register', 'args')

        mock_users_api.assert_called_with('args')
