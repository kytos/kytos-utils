"""kytos.utils.napps tests."""
import json
import re
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from unittest.mock import MagicMock, Mock, PropertyMock, call, patch
from urllib.error import HTTPError

from kytos.utils.exceptions import KytosException
from kytos.utils.napps import NAppsManager
from kytos.utils.settings import SKEL_PATH


# pylint: disable=protected-access, too-many-public-methods
class TestNapps(unittest.TestCase):
    """Test the class NAppsManager."""

    def setUp(self):
        """Execute steps before each tests."""
        self.napps_manager = NAppsManager()

    @staticmethod
    def get_napps_response_mock(napps=None):
        """Get mock to napps response."""
        if napps is None:
            napps = [["kytos", "mef_eline"], ["kytos", "of_lldp"]]
        response = json.dumps({"napps": napps})

        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = response
        mock_response.__enter__.return_value = mock_response
        return mock_response

    @patch('urllib.request.urlopen')
    def test_enabled_property(self, mock_urlopen):
        """Test enabled property."""
        data = MagicMock()
        data.read.return_value = '{"napps": "ABC", "installed_napps": "DEF"}'
        mock_urlopen.return_value = data

        self.assertEqual(str(self.napps_manager._enabled), 'ABC')

    def test_enabled_property__error(self):
        """Test enabled property to error case."""

        with self.assertRaises(SystemExit):
            # pylint: disable=pointless-statement
            self.napps_manager._enabled
            # pylint: enable=pointless-statement

        self.assertIsNone(self.napps_manager._NAppsManager__local_enabled)

    @patch('urllib.request.urlopen')
    def test_installed_property(self, mock_urlopen):
        """Test installed property."""
        data = MagicMock()
        data.read.return_value = '{"napps": "ABC", "installed_napps": "DEF"}'
        mock_urlopen.return_value = data

        self.assertEqual(str(self.napps_manager._installed), 'DEF')

    def test_installed_property__error(self):
        """Test installed property to error case."""

        with self.assertRaises(SystemExit):
            # pylint: disable=pointless-statement
            self.napps_manager._installed
            # pylint: enable=pointless-statement

        self.assertIsNone(self.napps_manager._NAppsManager__local_installed)

    def test_napp_id_property(self):
        """Test napp_id property."""
        self.napps_manager.user = 'user'
        self.napps_manager.napp = 'napp'

        self.assertEqual(self.napps_manager.napp_id, 'user/napp')

    def test_set_napp(self):
        """Test set_napp method."""
        self.napps_manager.set_napp('user', 'napp', 'version')

        self.assertEqual(self.napps_manager.user, 'user')
        self.assertEqual(self.napps_manager.napp, 'napp')
        self.assertEqual(self.napps_manager.version, 'version')

    def test_get_napps(self):
        """Test method get_napps used to find
        enabled and installed napps.
        """
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
        get_return = self.napps_manager._get_napps(mock_path)
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

        mock_prop_enabled = PropertyMock()
        with patch.object(NAppsManager, '_enabled', mock_prop_enabled):
            mock_prop_enabled.return_value = mock_path

            get_return = self.napps_manager.get_enabled_local()

            self.assertEqual(get_return[0][0], 'kytos')
            self.assertEqual(get_return[0][1], 'of_core')
            self.assertEqual(mock_prop_enabled.call_count, 1)

    def test_get_installed_local(self):
        """Test get_installed_local used to find
        installed napps in local machine"""
        # Mock kytos.json path
        mock_path = Mock()

        def glob_side_effect(args):
            """Path.glob to mock finding paths with kytos.json file."""
            self.assertEqual(args, "*/*/kytos.json")

            mock_path1 = Mock()
            mock_path1.parts = ['kytos', 'of_core', 'kytos.json']
            return [mock_path1]
        mock_path.glob = glob_side_effect

        mock_prop_installed = PropertyMock()
        with patch.object(NAppsManager, '_installed', mock_prop_installed):
            mock_prop_installed.return_value = mock_path

            get_return = self.napps_manager.get_installed_local()

            self.assertEqual(get_return[0][0], 'kytos')
            self.assertEqual(get_return[0][1], 'of_core')
            self.assertEqual(mock_prop_installed.call_count, 1)

    @patch('urllib.request.urlopen')
    def test_get_installed(self, mock_urlopen):
        """Test method get_installed to find all installed napps."""
        mock_urlopen.return_value = self.get_napps_response_mock()

        installed_napps = self.napps_manager.get_installed()

        self.assertEqual(len(installed_napps), 2)
        self.assertEqual(installed_napps[0], ("kytos", "mef_eline"))
        self.assertEqual(installed_napps[1], ("kytos", "of_lldp"))

    def test_get_installed__connection_error(self):
        """Test method get_installed to connection error case."""
        with self.assertRaises(KytosException) as context:
            self.napps_manager.get_installed()

        self.assertEqual('<urlopen error [Errno 111] Connection refused>',
                         str(context.exception))

    @patch('urllib.request.urlopen')
    def test_get_installed__error(self, mock_urlopen):
        """Test method get_installed with API error."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 500
        mock_urlopen.return_value = mock_response

        with self.assertRaises(KytosException) as context:
            self.napps_manager.get_installed()

        self.assertEqual('Error calling Kytos to check installed NApps.',
                         str(context.exception))

    @patch('urllib.request.urlopen')
    def test_get_enabled(self, mock_urlopen):
        """Test method get_enabled to find all enabled napps."""
        mock_urlopen.return_value = self.get_napps_response_mock()

        installed_napps = self.napps_manager.get_enabled()

        self.assertEqual(len(installed_napps), 2)
        self.assertEqual(installed_napps[0], ("kytos", "mef_eline"))
        self.assertEqual(installed_napps[1], ("kytos", "of_lldp"))

    def test_get_enabled__connection_error(self):
        """Test method get_enabled to connection error case."""
        with self.assertRaises(KytosException) as context:
            self.napps_manager.get_enabled()

        self.assertEqual('<urlopen error [Errno 111] Connection refused>',
                         str(context.exception))

    @patch('urllib.request.urlopen')
    def test_get_enabled__error(self, mock_urlopen):
        """Test method get_enabled with API error."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 500
        mock_urlopen.return_value = mock_response

        with self.assertRaises(KytosException) as context:
            self.napps_manager.get_enabled()

        self.assertEqual('Error calling Kytos to check enabled NApps.',
                         str(context.exception))

    @patch('urllib.request.urlopen')
    def test_is_enabled(self, mock_urlopen):
        """Test is_enabled method."""
        mock_urlopen.return_value = self.get_napps_response_mock()

        self.napps_manager.user = 'kytos'
        self.napps_manager.napp = 'mef_eline'

        self.assertTrue(self.napps_manager.is_enabled())

    @patch('urllib.request.urlopen')
    def test_is_installed(self, mock_urlopen):
        """Test is_installed method."""
        mock_urlopen.return_value = self.get_napps_response_mock()

        self.napps_manager.user = 'kytos'
        self.napps_manager.napp = 'mef_eline'

        self.assertTrue(self.napps_manager.is_installed())

    @patch('urllib.request.urlopen')
    def test_get_disabled(self, mock_urlopen):
        """Test get_disabled method."""
        enabled = [["kytos", "mef_eline"]]
        mock_urlopen.side_effect = [self.get_napps_response_mock(),
                                    self.get_napps_response_mock(enabled)]

        disabled = self.napps_manager.get_disabled()

        self.assertEqual(disabled, [('kytos', 'of_lldp')])

    @patch('urllib.request.urlopen')
    def test_dependencies(self, mock_urlopen):
        """Test dependencies method."""
        napps = {"napp_dependencies": ["kytos/mef_eline", "kytos/of_lldp"]}
        data = MagicMock()
        data.read.return_value = json.dumps(napps)
        mock_urlopen.return_value = data

        dependencies = self.napps_manager.dependencies()

        expected_dependencies = [('kytos', 'mef_eline'), ('kytos', 'of_lldp')]
        self.assertEqual(dependencies, expected_dependencies)

    @patch('urllib.request.urlopen')
    def test_get_description(self, mock_urlopen):
        """Test get_description method."""
        data = MagicMock()
        data.read.return_value = '{"description": "ABC"}'
        mock_urlopen.return_value = data

        description = self.napps_manager.get_description()

        self.assertEqual(description, 'ABC')

    @patch('urllib.request.urlopen')
    def test_get_version(self, mock_urlopen):
        """Test get_version method."""
        data = MagicMock()
        data.read.return_value = '{"version": "123"}'
        mock_urlopen.return_value = data

        version = self.napps_manager.get_version()

        self.assertEqual(version, '123')

    @patch('urllib.request.urlopen')
    def test_get_napp_key(self, mock_urlopen):
        """Test _get_napp_key method."""
        data = MagicMock()
        data.read.return_value = '{"key": "ABC"}'
        mock_urlopen.return_value = data

        self.napps_manager.user = 'kytos'
        self.napps_manager.napp = 'mef_eline'

        meta_key = self.napps_manager._get_napp_key('key')

        self.assertEqual(meta_key, 'ABC')

    @patch('urllib.request.urlopen')
    def test_disable(self, mock_urlopen):
        """Test disable method."""
        data = MagicMock()
        data.read.return_value = '{}'
        mock_urlopen.return_value = data

        self.napps_manager.user = 'kytos'
        self.napps_manager.napp = 'mef_eline'

        self.napps_manager.disable()

        uri = self.napps_manager._kytos_api + self.napps_manager._NAPP_DISABLE
        uri = uri.format('kytos', 'mef_eline')

        mock_urlopen.assert_called_with(uri)

    @patch('kytos.utils.napps.LOG')
    @patch('urllib.request.urlopen')
    def test_disable__error(self, *args):
        """Test disable method to error case."""
        (mock_urlopen, mock_logger) = args
        http_errors = [HTTPError('url', 400, 'msg', 'hdrs', MagicMock()),
                       HTTPError('url', 500, 'msg', 'hdrs', MagicMock())]
        mock_urlopen.side_effect = http_errors

        self.napps_manager.disable()
        self.napps_manager.disable()

        self.assertEqual(mock_logger.error.call_count, 2)

    @patch('urllib.request.urlopen')
    def test_enable(self, mock_urlopen):
        """Test enable method."""
        data = MagicMock()
        data.read.return_value = '{}'
        mock_urlopen.return_value = data

        self.napps_manager.user = 'kytos'
        self.napps_manager.napp = 'mef_eline'

        self.napps_manager.enable()

        uri = self.napps_manager._kytos_api + self.napps_manager._NAPP_ENABLE
        uri = uri.format('kytos', 'mef_eline')

        mock_urlopen.assert_called_with(uri)

    @patch('kytos.utils.napps.LOG')
    @patch('urllib.request.urlopen')
    def test_enable__error(self, *args):
        """Test enable method to error case."""
        (mock_urlopen, mock_logger) = args
        http_errors = [HTTPError('url', 400, 'msg', 'hdrs', MagicMock()),
                       HTTPError('url', 500, 'msg', 'hdrs', MagicMock())]
        mock_urlopen.side_effect = http_errors

        self.napps_manager.enable()
        self.napps_manager.enable()

        self.assertEqual(mock_logger.error.call_count, 2)

    @patch('urllib.request.urlopen')
    def test_enabled_dir(self, mock_urlopen):
        """Test enabled_dir method."""
        data = MagicMock()
        data.read.return_value = '{"napps": "ABC", "installed_napps": "DEF"}'
        mock_urlopen.return_value = data

        self.napps_manager.user = 'kytos'
        self.napps_manager.napp = 'mef_eline'

        enabled_dir = self.napps_manager.enabled_dir()
        self.assertEqual(str(enabled_dir), 'ABC/kytos/mef_eline')

    @patch('urllib.request.urlopen')
    def test_installed_dir(self, mock_urlopen):
        """Test installed_dir method."""
        data = MagicMock()
        data.read.return_value = '{"napps": "ABC", "installed_napps": "DEF"}'
        mock_urlopen.return_value = data

        self.napps_manager.user = 'kytos'
        self.napps_manager.napp = 'mef_eline'

        installed_dir = self.napps_manager.installed_dir()
        self.assertEqual(str(installed_dir), 'DEF/kytos/mef_eline')

    @patch('urllib.request.urlopen')
    def test_remote_uninstall(self, mock_urlopen):
        """Test remote_uninstall method."""
        data = MagicMock()
        data.read.return_value = '{}'
        mock_urlopen.return_value = data

        self.napps_manager.user = 'kytos'
        self.napps_manager.napp = 'mef_eline'

        self.napps_manager.remote_uninstall()

        uninstall_uri = self.napps_manager._NAPP_UNINSTALL
        uri = self.napps_manager._kytos_api + uninstall_uri
        uri = uri.format('kytos', 'mef_eline')

        mock_urlopen.assert_called_with(uri)

    @patch('kytos.utils.napps.LOG')
    @patch('urllib.request.urlopen')
    def test_remote_uninstall__error(self, *args):
        """Test remote_uninstall method to error case."""
        (mock_urlopen, mock_logger) = args
        http_errors = [HTTPError('url', 400, 'msg', 'hdrs', MagicMock()),
                       HTTPError('url', 500, 'msg', 'hdrs', MagicMock())]
        mock_urlopen.side_effect = http_errors

        self.napps_manager.remote_uninstall()
        self.napps_manager.remote_uninstall()

        self.assertEqual(mock_logger.error.call_count, 2)

    @patch('urllib.request.urlopen')
    def test_remote_install(self, mock_urlopen):
        """Test remote_install method."""
        data = MagicMock()
        data.read.return_value = '{}'
        mock_urlopen.return_value = data

        self.napps_manager.user = 'kytos'
        self.napps_manager.napp = 'mef_eline'

        self.napps_manager.remote_install()

        install_uri = self.napps_manager._NAPP_INSTALL
        uri = self.napps_manager._kytos_api + install_uri
        uri = uri.format('kytos', 'mef_eline')

        mock_urlopen.assert_called_with(uri)

    def test_valid_name(self):
        """Test valid_name method."""
        valid_name = self.napps_manager.valid_name('username')
        invalid_name = self.napps_manager.valid_name('_username')

        self.assertTrue(valid_name)
        self.assertFalse(invalid_name)

    @patch('jinja2.Environment.get_template')
    def test_render_template(self, mock_get_template):
        """Test render_template method."""
        template = MagicMock()
        mock_get_template.return_value = template

        self.napps_manager.render_template('', 'filename', 'context')

        mock_get_template.assert_called_with('filename')
        template.render.assert_called_with('context')

    @patch('kytos.utils.napps.NAppsClient')
    def test_search(self, mock_napps_client):
        """Test search method."""
        napp_1 = {'username': 'kytos', 'name': 'mef_eline', 'description': '',
                  'tags': ['A', 'B']}
        napp_2 = {'username': '0_kytos', 'name': 'any', 'description': '',
                  'tags': ['A', 'B']}
        napps_client = MagicMock()
        napps_client.get_napps.return_value = [napp_1, napp_2]
        mock_napps_client.return_value = napps_client

        # pattern to match strings that start with letters
        pattern = re.compile('^[a-z]+')
        napps = self.napps_manager.search(pattern)

        self.assertEqual(napps, [napp_1])

    @patch('os.makedirs')
    @patch('builtins.open')
    @patch('builtins.input')
    @patch('kytos.utils.napps.NAppsManager.render_template')
    def test_create_napp(self, *args):
        """Test create_napp method."""
        (mock_render_template, mock_input, _, mock_mkdirs) = args
        mock_input.side_effect = ['username', 'napp', None]

        self.napps_manager.create_napp()

        tmpl_path = SKEL_PATH / 'napp-structure/username/napp'
        description = '# TODO: <<<< Insert your NApp description here >>>>'
        context = {'username': 'username', 'napp': 'napp',
                   'description': description}

        calls = []
        for tmp in ['__init__.py', 'main.py', '.gitignore', 'kytos.json',
                    'README.rst', 'settings.py']:
            calls.append(call(tmpl_path, '{}.template'.format(tmp), context))
        calls.append(call('{}/ui'.format(tmpl_path), 'README.rst.template',
                          context))

        mock_mkdirs.assert_has_calls([call('username', exist_ok=True),
                                      call('username/napp'),
                                      call('username/napp/ui/k-info-panel'),
                                      call('username/napp/ui/k-toolbar'),
                                      call('username/napp/ui/k-action-menu')])
        mock_render_template.assert_has_calls(calls, any_order=True)

    def test_check_module(self):
        """Test _check_module method."""
        folder = MagicMock()
        folder.exists.return_value = False

        self.napps_manager._check_module(folder)

        folder.mkdir.assert_called()
        (folder / '__init__.py').touch.assert_called()

    @patch('pathspec.pathspec.PathSpec.match_tree')
    @patch('tarfile.TarFile.add')
    @patch('os.remove')
    @patch('os.walk')
    @patch('os.getcwd')
    @patch('builtins.open')
    def test_build_napp_package(self, *args):
        """Test build_napp_package method."""
        (_, mock_getcwd, mock_walk, _, mock_add, mock_match_tree) = args
        with tempfile.TemporaryDirectory() as tmp_dir:
            mock_getcwd.return_value = tmp_dir

            files = ['username/napp/A', 'username/napp/B', 'username/napp/C']
            mock_walk.return_value = [(tmp_dir, ['username/napp/.git'], files)]

            mock_match_tree.return_value = ['username/napp/C']

            self.napps_manager.build_napp_package('username/napp')

            calls = [call(PurePosixPath('username/napp/A')),
                     call(PurePosixPath('username/napp/B'))]
            mock_add.assert_has_calls(calls)

    @patch('ruamel.yaml.YAML.load', return_value='openapi')
    @patch('pathlib.Path.open')
    @patch('builtins.open')
    def test_create_metadata(self, *args):
        """Test create_metadata method."""
        (mock_open, _, _) = args
        enter_file_1 = MagicMock()
        enter_file_1.read.return_value = '{}'

        enter_file_2 = MagicMock()
        enter_file_2.read.return_value = 'readme'

        mock_open.return_value.__enter__.side_effect = [enter_file_1,
                                                        enter_file_2]

        metadata = self.napps_manager.create_metadata()

        self.assertEqual(metadata, {'readme': 'readme',
                                    'OpenAPI_Spec': '"openapi"'})

    @patch('kytos.utils.napps.NAppsClient')
    @patch('kytos.utils.napps.NAppsManager.build_napp_package')
    @patch('kytos.utils.napps.NAppsManager.create_metadata')
    @patch('kytos.utils.napps.NAppsManager.prepare')
    def test_upload(self, *args):
        """Test upload method."""
        (mock_prepare, mock_create, mock_build, mock_napps_client) = args
        mock_create.return_value = {'name': 'ABC'}
        mock_build.return_value = 'package'
        napps_client = MagicMock()
        mock_napps_client.return_value = napps_client

        self.napps_manager.upload()

        mock_prepare.assert_called()
        mock_create.assert_called()
        mock_build.assert_called_with('ABC')
        napps_client.upload_napp.assert_called_with({'name': 'ABC'}, 'package')

    @patch('kytos.utils.napps.NAppsClient')
    def test_delete(self, mock_napps_client):
        """Test delete method."""
        napps_client = MagicMock()
        mock_napps_client.return_value = napps_client

        self.napps_manager.user = 'kytos'
        self.napps_manager.napp = 'mef_eline'

        self.napps_manager.delete()

        napps_client.delete.assert_called_with('kytos', 'mef_eline')

    @patch('sys.exit')
    @patch('kytos.utils.napps.OpenAPI')
    @patch('kytos.utils.napps.NAppsManager._ask_openapi', return_value=True)
    def test_prepare(self, *args):
        """Test prepare method."""
        (_, mock_openapi, _) = args
        self.napps_manager.prepare()

        napp_path = Path()
        tpl_path = SKEL_PATH / 'napp-structure/username/napp'
        mock_openapi.assert_called_with(napp_path, tpl_path)
        mock_openapi.return_value.render_template.assert_called()

    @patch('pathlib.Path.exists')
    @patch('builtins.input')
    def test_ask_openapi(self, *args):
        """Test _ask_openapi method."""
        (mock_input, mock_exists) = args
        mock_input.side_effect = ['', '', 'yes', 'no']
        mock_exists.side_effect = [True, False, False, False]

        for expected in [False, True, True, False]:
            response = self.napps_manager._ask_openapi()
            self.assertEqual(response, expected)

    @patch('kytos.utils.napps.NAppsClient')
    def test_reload(self, mock_napps_client):
        """Test reload method."""
        napps_client = MagicMock()
        mock_napps_client.return_value = napps_client

        napps = []
        self.napps_manager.reload(napps)

        napps_client.reload_napps.assert_called_with(napps)
