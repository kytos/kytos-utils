"""kytos.cli.commands.web.parser tests."""
import sys
import unittest
from unittest.mock import patch

from kytos.cli.commands.web.parser import call, parse
from kytos.utils.exceptions import KytosException


class TestWebParser(unittest.TestCase):
    """Test the WebAPI parser methods."""

    @staticmethod
    @patch('kytos.cli.commands.web.parser.call')
    @patch('kytos.cli.commands.web.parser.docopt', return_value='args')
    def test_parse(*args):
        """Test parse method."""
        (_, mock_call) = args
        with patch.object(sys, 'argv', ['A', 'B', 'C']):
            parse('argv')

            mock_call.assert_called_with('C', 'args')

    @staticmethod
    @patch('sys.exit')
    @patch('kytos.cli.commands.web.parser.call')
    @patch('kytos.cli.commands.web.parser.docopt', return_value='args')
    def test_parse__error(*args):
        """Test parse method to error case."""
        (_, mock_call, mock_exit) = args
        mock_call.side_effect = KytosException
        with patch.object(sys, 'argv', ['A', 'B', 'C']):
            parse('argv')

            mock_exit.assert_called()

    @staticmethod
    @patch('kytos.cli.commands.web.api.WebAPI.update')
    @patch('kytos.utils.config.KytosConfig')
    def test_call(*args):
        """Test call method."""
        (_, mock_web_api) = args
        call('update', 'args')

        mock_web_api.assert_called_with('args')
