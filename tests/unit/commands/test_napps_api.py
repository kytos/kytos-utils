"""kytos.cli.commands.napps.api.NAppsAPI tests."""
import unittest
from unittest.mock import MagicMock, call, patch
from urllib.error import HTTPError

import requests

from kytos.cli.commands.napps.api import NAppsAPI
from kytos.utils.exceptions import KytosException


# pylint: disable=too-many-public-methods
class TestNAppsAPI(unittest.TestCase):
    """Test the class NAppsAPI."""

    def setUp(self):
        """Execute steps before each tests."""
        self.napps_api = NAppsAPI()

    @patch('kytos.cli.commands.napps.api.NAppsManager')
    def test_disable__all(self, mock_napps_manager):
        """Test disable method to all napps."""
        napp = ('user', 'napp', 'version')

        mgr = MagicMock()
        mgr.get_enabled.return_value = [napp]
        mock_napps_manager.return_value = mgr

        args = {'all': True}
        self.napps_api.disable(args)

        mgr.set_napp.assert_called_with(*napp)
        mgr.disable.assert_called()

    @patch('kytos.cli.commands.napps.api.NAppsManager')
    def test_disable__any(self, mock_napps_manager):
        """Test disable method to any napp."""
        mgr = MagicMock()
        mock_napps_manager.return_value = mgr

        napp = ('user', 'napp', 'version')
        args = {'all': False, '<napp>': [napp]}
        self.napps_api.disable(args)

        mgr.set_napp.assert_called_with(*napp)
        mgr.disable.assert_called()

    def test_disable_napp(self):
        """Test disable_napp method."""
        mgr = MagicMock()
        mgr.is_enabled.side_effect = [True, False]

        self.napps_api.disable_napp(mgr)
        self.napps_api.disable_napp(mgr)

        mgr.disable.assert_called_once()

    @patch('kytos.cli.commands.napps.api.NAppsManager')
    def test_enable__all(self, mock_napps_manager):
        """Test enable method to all napps."""
        napp = ('user', 'napp', 'version')

        mgr = MagicMock()
        mgr.is_enabled.return_value = False
        mgr.get_disabled.return_value = [napp]
        mock_napps_manager.return_value = mgr

        args = {'all': True}
        self.napps_api.enable(args)

        mgr.set_napp.assert_called_with(*napp)
        mgr.enable.assert_called()

    @patch('kytos.cli.commands.napps.api.NAppsManager')
    def test_enable__any(self, mock_napps_manager):
        """Test enable method to any napp."""
        mgr = MagicMock()
        mgr.is_enabled.return_value = False
        mock_napps_manager.return_value = mgr

        napp = ('user', 'napp', 'version')
        args = {'all': False, '<napp>': [napp]}
        self.napps_api.enable(args)

        mgr.set_napp.assert_called_with(*napp)
        mgr.enable.assert_called()

    def test_enable_napp__success(self):
        """Test enable_napp method to success case."""
        mgr = MagicMock()
        mgr.is_enabled.return_value = False

        self.napps_api.enable_napp(mgr)

        mgr.enable.assert_called()

    def test_enable_napp__error(self):
        """Test enable_napp method to error case."""
        mgr = MagicMock()
        mgr.is_enabled.return_value = True

        self.napps_api.enable_napp(mgr)

        mgr.enable.assert_not_called()

    @patch('kytos.cli.commands.napps.api.NAppsManager')
    @patch('kytos.cli.commands.napps.api.NAppsAPI.enable_napp')
    def test_enable_napps(self, *args):
        """Test enable_napps method."""
        (mock_enable_napp, mock_napps_manager) = args
        mgr = MagicMock()
        mock_napps_manager.return_value = mgr

        napp = ('user', 'napp', 'version')
        self.napps_api.enable_napps([napp])

        mgr.set_napp.assert_called_with(*napp)
        mock_enable_napp.assert_called_with(mgr)

    @patch('kytos.cli.commands.napps.api.NAppsManager.create_napp')
    def test_create(self, mock_create_napp):
        """Test create method."""
        self.napps_api.create({})

        mock_create_napp.assert_called()

    @patch('kytos.cli.commands.napps.api.NAppsManager.upload')
    def test_upload(self, mock_upload):
        """Test upload method."""
        self.napps_api.upload({})

        mock_upload.assert_called()

    @patch('kytos.cli.commands.napps.api.NAppsManager')
    def test_uninstall(self, mock_napps_manager):
        """Test uninstall method."""
        mgr = MagicMock()
        mgr.is_installed.return_value = True
        mock_napps_manager.return_value = mgr

        napp = ('user', 'napp', 'version')
        args = {'<napp>': [napp]}
        self.napps_api.uninstall(args)

        mgr.set_napp.assert_called_with(*napp)
        mgr.remote_uninstall.assert_called()

    @patch('kytos.cli.commands.napps.api.NAppsManager')
    def test_install(self, mock_napps_manager):
        """Test install method."""
        mgr = MagicMock()
        mgr.is_installed.return_value = False
        mock_napps_manager.return_value = mgr

        napp = ('user', 'napp', 'version')
        args = {'<napp>': [napp]}
        self.napps_api.install(args)

        mgr.set_napp.assert_called_with(*napp)
        mgr.remote_install.assert_called()

    @patch('kytos.cli.commands.napps.api.NAppsManager')
    def test_install_napps(self, mock_napps_manager):
        """Test prepare method."""
        mgr = MagicMock()
        mgr.is_installed.return_value = False
        mock_napps_manager.return_value = mgr

        napp = ('user', 'napp', 'version')
        self.napps_api.install_napps([napp])

        mgr.set_napp.assert_called_with(*napp)
        mgr.remote_install.assert_called()

    @patch('kytos.cli.commands.napps.api.NAppsManager')
    def test_install_napp(self, mock_napps_manager):
        """Test install_napp method."""
        mgr = MagicMock()
        mock_napps_manager.return_value = mgr

        self.napps_api.install_napp(mgr)

        mgr.remote_install.assert_called()

    @patch('kytos.utils.napps.NAppsManager')
    def test_install_napp_error_404(self, mgr):
        """Test install_napp method."""
        mgr = MagicMock()

        url = 'napps.kytos.io'
        msg = 'The NApp were not found at server.'
        code = 404
        hdrs = 'The HTTP response headers'
        filep = None
        mgr.remote_install.side_effect = HTTPError(url, code, msg, hdrs, filep)
        with self.assertRaises(KytosException):
            self.napps_api.install_napp(mgr)

    @patch('kytos.utils.napps.NAppsManager')
    def test_install_napp_error_400(self, mgr):
        """Test install_napp method."""
        mgr = MagicMock()

        url = 'napps.kytos.io'
        msg = 'The NApp were not found at server.'
        code = 400
        hdrs = 'The HTTP response headers'
        filep = None
        mgr.remote_install.side_effect = HTTPError(url, code, msg, hdrs, filep)

        with self.assertRaises(KytosException):
            self.napps_api.install_napp(mgr)

    @patch('kytos.cli.commands.napps.api.NAppsManager.search')
    @patch('kytos.cli.commands.napps.api.NAppsAPI._print_napps')
    def test_search(self, *args):
        """Test search method."""
        (mock_print, mock_search) = args
        mock_search.return_value = [{'username': 'kytos', 'name': 'mef_eline',
                                     'description': '', 'tags': ['A', 'B']}]

        args = {'<pattern>': '^[a-z]+'}
        self.napps_api.search(args)

        mock_print.assert_called_with({(('kytos', 'mef_eline'), '')})

    @patch('os.popen')
    @patch('builtins.print')
    @patch('kytos.cli.commands.napps.api.NAppsManager')
    def test_print_napps(self, *args):
        """Test _print_napps method."""
        (mock_napps_manager, mock_print, mock_popen) = args
        napps = [('kytos', 'mef_eline')]

        mock_test = MagicMock()
        mock_test.read.return_value = '1000 1000'
        mock_popen.return_value = mock_test

        mgr = MagicMock()
        mgr.get_enabled.return_value = napps
        mgr.get_installed.return_value = napps
        mock_napps_manager.return_value = mgr

        # pylint: disable=protected-access
        self.napps_api._print_napps({(('kytos', 'mef_eline'), 'desc')})
        # pylint: enable=protected-access

        mock_print.assert_has_calls([call(' [ie]  | kytos/mef_eline | desc')])

    @patch('kytos.cli.commands.napps.api.NAppsManager')
    @patch('kytos.cli.commands.napps.api.NAppsAPI.print_napps')
    def test_list(self, *args):
        """Test list method."""
        (mock_print, mock_napps_manager) = args
        napps = [('kytos', 'mef_eline')]

        mgr = MagicMock()
        mgr.get_version.return_value = '123'
        mgr.get_description.return_value = 'desc'
        mgr.get_enabled.return_value = napps
        mgr.get_installed.return_value = napps
        mock_napps_manager.return_value = mgr

        self.napps_api.list({})

        expected = [('[ie]', 'kytos/mef_eline:123', 'desc')]
        mock_print.assert_called_with(expected)

    @patch('kytos.cli.commands.napps.api.NAppsManager')
    def test_delete(self, mock_napps_manager):
        """Test delete method."""
        mgr = MagicMock()
        mock_napps_manager.return_value = mgr

        napp = ('user', 'napp', 'version')
        args = {'<napp>': [napp]}
        self.napps_api.delete(args)

        mgr.set_napp.assert_called_with(*napp)
        mgr.delete.assert_called()

    @patch('kytos.cli.commands.napps.api.LOG')
    @patch('kytos.cli.commands.napps.api.NAppsManager')
    def test_delete__error(self, *args):
        """Test delete method to error case."""
        (mock_napps_manager, mock_logger) = args
        response_1 = MagicMock(status_code=405, content='{"error": "info"}')
        response_2 = MagicMock(status_code=500, content='{"error": "info"}')
        mgr = MagicMock()
        mgr.delete.side_effect = [requests.HTTPError(response=response_1),
                                  requests.HTTPError(response=response_2)]
        mock_napps_manager.return_value = mgr

        napp = ('user', 'napp', 'version')
        args = {'<napp>': [napp]}

        self.napps_api.delete(args)
        self.napps_api.delete(args)

        self.assertEqual(mock_logger.error.call_count, 2)

    @patch('kytos.cli.commands.napps.api.NAppsManager')
    def test_prepare(self, mock_napps_manager):
        """Test prepare method."""
        mgr = MagicMock()
        mock_napps_manager.return_value = mgr

        self.napps_api.prepare(None)

        mgr.prepare.assert_called()

    @patch('kytos.cli.commands.napps.api.NAppsManager')
    def test_reload__all(self, mock_napps_manager):
        """Test reload method to all napps."""
        mgr = MagicMock()
        mock_napps_manager.return_value = mgr

        args = {'all': True}
        self.napps_api.reload(args)

        mgr.reload.assert_called()

    @patch('kytos.cli.commands.napps.api.NAppsManager')
    def test_reload__any(self, mock_napps_manager):
        """Test reload method to any napp."""
        mgr = MagicMock()
        mock_napps_manager.return_value = mgr

        napps = ['A', 'B', 'C']
        args = {'all': False, '<napp>': napps}
        self.napps_api.reload(args)

        mgr.reload.assert_called_with(napps)

    @patch('kytos.cli.commands.napps.api.LOG')
    @patch('kytos.cli.commands.napps.api.NAppsManager')
    def test_reload__error(self, *args):
        """Test reload method to error case."""
        (mock_napps_manager, mock_logger) = args
        response = MagicMock(status_code=500, content='{"error": "info"}')
        mgr = MagicMock()
        mgr.reload.side_effect = requests.HTTPError(response=response)
        mock_napps_manager.return_value = mgr

        args = {'all': True}
        self.napps_api.reload(args)

        self.assertEqual(mock_logger.error.call_count, 1)
