"""kytos.utils.openapi tests."""
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from kytos.utils.openapi import OpenAPI

MAIN_FILE = '''
    from kytos.core import KytosNApp, log

    class Main(KytosNApp):
        def setup(self):
            pass

        def execute(self):
            pass

        def shutdown(self):
            pass

        @rest("/any", methods=["GET"])
        def any(self):
            """docstring"""
            pass
'''


# pylint: disable=arguments-differ, protected-access
class TestOpenAPI(unittest.TestCase):
    """Test the class OpenAPI."""

    @patch('builtins.open')
    def setUp(self, mock_open):
        """Execute steps before each tests."""
        data = MagicMock()
        data.read.return_value = '{"username": "kytos", "name": "mef_eline"}'
        enter_data = MagicMock()
        enter_data.__enter__.return_value = data
        mock_open.return_value = enter_data

        napp_path = Path('')
        tpl_path = Path('')
        self.open_api = OpenAPI(napp_path, tpl_path)

    @patch('pathlib.Path.open')
    @patch('kytos.utils.openapi.OpenAPI._save')
    def test_render_template(self, *args):
        """Test render_template method."""
        (mock_save, mock_open) = args
        open_file = MagicMock()
        open_file.read.return_value = MAIN_FILE
        mock_open.return_value = open_file

        self.open_api.render_template()

        description = 'TODO write/remove the description'
        path_dict = {'get': {'summary': 'docstring',
                             'description': description}}
        expected = {'napp': {'username': 'kytos', 'name': 'mef_eline'},
                    'paths': {'/api/kytos/mef_eline/any': path_dict}}
        mock_save.assert_called_with(expected)

    @patch('pathlib.Path.open')
    def test_read_napp_info(self, mock_open):
        """Test _read_napp_info method."""
        open_file = MagicMock()
        open_file.read.return_value = '{"info": "ABC"}'
        mock_open.return_value = open_file

        response = self.open_api._read_napp_info()

        self.assertEqual(response, {'info': 'ABC'})

    @patch('pathlib.Path.open')
    @patch('jinja2.Environment.get_template')
    def test_save(self, *args):
        """Test _save method."""
        (mock_get_template, mock_open) = args
        tmpl = MagicMock()
        tmpl.render.return_value = 'content'
        mock_get_template.return_value = tmpl

        enter_openapi = MagicMock()
        mock_open.return_value.__enter__.return_value = enter_openapi

        self.open_api._save('context')

        tmpl.render.assert_called_with('context')
        enter_openapi.write.assert_called_with('content')
