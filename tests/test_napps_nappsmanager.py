"""kytos.utils.napps.NAppsManager tests."""
import unittest
from unittest.mock import MagicMock, Mock, PropertyMock, patch

from kytos.utils.exceptions import KytosException
from kytos.utils.napps import NAppsManager


class TestNapps(unittest.TestCase):
    """Test the class APIServer."""

    def setUp(self):
        """Instantiate a APIServer."""

    def test_get_napps(self):
        """Test method get_napps used to find
        enabled and installed napps.
        """
        napps_manager = NAppsManager()
        mock_path = Mock()

        def glob_side_effect(args):
            """Path.glob to mock finding paths with kytos.json file."""
            self.assertEqual(args, "*/*/kytos.json")

            mock_path1 = Mock()
            mock_path1.parts = ['kytos', 'of_core', 'kytos.json']

            mock_path2 = Mock()
            mock_path2.parts = ['kytos', 'of_lldp', 'kytos.json']

            return [mock_path1, mock_path2]

        mock_path.glob = glob_side_effect

        # pylint: disable=protected-access
        get_return = napps_manager._get_napps(mock_path)
        self.assertEqual(get_return[0][0], 'kytos')
        self.assertEqual(get_return[0][1], 'of_core')
        self.assertEqual(get_return[1][0], 'kytos')
        self.assertEqual(get_return[1][1], 'of_lldp')

    def test_get_enabled_local(self):
        """Test get_enabled_local used to find
        enabled napps in local machine"""
        # Mock kytos.json path
        mock_path = Mock()

        def glob_side_effect(args):
            """Path.glob to mock finding paths with kytos.json file."""
            self.assertEqual(args, "*/*/kytos.json")

            mock_path1 = Mock()
            mock_path1.parts = ['kytos', 'of_core', 'kytos.json']
            return [mock_path1]
        mock_path.glob = glob_side_effect

        # Mock _enabled Path property
        mock_prop_enabled = PropertyMock()
        with patch.object(NAppsManager, '_enabled', mock_prop_enabled):
            mock_prop_enabled.return_value = mock_path

            # Call the get_enabled_local to test
            napps_manager = NAppsManager()
            get_return = napps_manager.get_enabled_local()
            self.assertEqual(get_return[0][0], 'kytos')
            self.assertEqual(get_return[0][1], 'of_core')

            self.assertEqual(mock_prop_enabled.call_count, 1)

    @patch('urllib.request.urlopen')
    def test_get_installed(self, mock_urlopen):
        """Test method get_installed to find all installed napps.
        """
        # Mocking the API call
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = \
            '{"napps": [["kytos", "mef_eline"], ["kytos", "of_lldp"]]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Call the get_installed method
        napps_manager = NAppsManager()
        installed_napps = napps_manager.get_installed()

        self.assertEqual(len(installed_napps), 2)
        self.assertEqual(installed_napps[0], ("kytos", "mef_eline"))
        self.assertEqual(installed_napps[1], ("kytos", "of_lldp"))

    @patch('urllib.request.urlopen')
    def test_get_installed__error(self, mock_urlopen):
        """Test method get_installed with API error
        """
        # Mocking the API call
        mock_response = MagicMock()
        mock_response.getcode.return_value = 500
        mock_urlopen.return_value = mock_response

        # Call the get_installed method
        napps_manager = NAppsManager()
        with self.assertRaises(KytosException) as context:
            napps_manager.get_installed()

        self.assertEqual('Error calling Kytos to check installed NApps.',
                         str(context.exception))

    @patch('urllib.request.urlopen')
    def test_get_enabled(self, mock_urlopen):
        """Test method get_enabled to find all enabled napps.
        """
        # Mocking the API call
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = \
            '{"napps": [["kytos", "mef_eline"], ' '["kytos", "of_lldp"]]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Call the get_installed method
        napps_manager = NAppsManager()
        installed_napps = napps_manager.get_enabled()

        self.assertEqual(len(installed_napps), 2)
        self.assertEqual(installed_napps[0], ("kytos", "mef_eline"))
        self.assertEqual(installed_napps[1], ("kytos", "of_lldp"))

    @patch('urllib.request.urlopen')
    def test_get_enabled__error(self, mock_urlopen):
        """Test method get_enabled with API error
        """
        # Mocking the API call
        mock_response = MagicMock()
        mock_response.getcode.return_value = 500
        mock_urlopen.return_value = mock_response

        # Call the get_installed method
        napps_manager = NAppsManager()
        with self.assertRaises(KytosException) as context:
            napps_manager.get_enabled()

        self.assertEqual('Error calling Kytos to check enabled NApps.',
                         str(context.exception))
