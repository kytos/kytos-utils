"""kytos.cli.commands.napps.parser tests."""
import sys
import unittest
from unittest.mock import patch

from kytos.cli.commands.napps.parser import (call, parse, parse_napp,
                                             parse_napps)
from kytos.utils.exceptions import KytosException


class TestNappsParser(unittest.TestCase):
    """Test the NappsAPI parser methods."""

    @staticmethod
    @patch('kytos.cli.commands.napps.parser.call')
    @patch('kytos.cli.commands.napps.parser.docopt', return_value='args')
    def test_parse(*args):
        """Test parse method."""
        (_, mock_call) = args
        with patch.object(sys, 'argv', ['A', 'B', 'C']):
            parse('argv')

            mock_call.assert_called_with('C', 'args')

    @staticmethod
    @patch('sys.exit')
    @patch('kytos.cli.commands.napps.parser.call')
    @patch('kytos.cli.commands.napps.parser.docopt', return_value='args')
    def test_parse__error(*args):
        """Test parse method to error case."""
        (_, mock_call, mock_exit) = args
        mock_call.side_effect = KytosException
        with patch.object(sys, 'argv', ['A', 'B', 'C']):
            parse('argv')

            mock_exit.assert_called()

    @staticmethod
    @patch('kytos.cli.commands.napps.api.NAppsAPI.install')
    @patch('kytos.utils.config.KytosConfig')
    def test_call(*args):
        """Test call method."""
        (_, mock_napps_api) = args
        call_args = {'<napp>': 'all'}
        call('install', call_args)

        mock_napps_api.assert_called_with(call_args)

    def test_parse_napps__all(self):
        """Test parse_napps method to all napps."""
        napp_ids = ['all']
        napps = parse_napps(napp_ids)

        self.assertEqual(napps, 'all')

    def test_parse_napps__any(self):
        """Test parse_napps method to any napp."""
        napp_ids = ['user/napp:version']
        napps = parse_napps(napp_ids)

        self.assertEqual(napps, [('user', 'napp', 'version')])

    def test_parse_napp__success(self):
        """Test parse_napp method to success case."""
        napp = 'user/napp:version'
        groups = parse_napp(napp)

        self.assertEqual(groups, ('user', 'napp', 'version'))

    def test_parse_napp__error(self):
        """Test parse_napp method to error case."""
        napp = 'usernappversion'
        with self.assertRaises(KytosException):
            parse_napp(napp)
