"""kytos.utils.client tests."""
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from kytos.utils.client import CommonClient, NAppsClient, UsersClient
from kytos.utils.config import KytosConfig


class TestCommonClient(unittest.TestCase):
    """Test the class CommonClient."""

    def setUp(self):
        """Execute steps before each tests."""
        self.common_client = CommonClient()

    @patch('requests.get')
    def test_make_request(self, mock_requests_get):
        """Test make_request method."""
        data = MagicMock()
        self.common_client.make_request('endpoint', json=data)

        mock_requests_get.assert_called_with('endpoint', json=data)

    @patch('requests.get')
    def test_make_request__package(self, mock_requests_get):
        """Test make_request method with package."""
        data = MagicMock()
        self.common_client.make_request('endpoint', package='any', json=data)

        mock_requests_get.assert_called_with('endpoint', data=data,
                                             files={'file': 'any'})


# pylint: disable=protected-access
class TestNAppsClient(unittest.TestCase):
    """Test the class NAppsClient."""

    def setUp(self):
        """Execute steps before each tests."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = '{}.kytosrc'.format(tmp_dir)
            kytos_config = KytosConfig(config_file)
            kytos_config.save_token('user', 'token')

        self.napps_client = NAppsClient()
        self.napps_client._config = kytos_config.config
        self.napps_client._config.set('kytos', 'api', 'endpoint')
        self.napps_client._config.set('napps', 'api', 'endpoint')

    @staticmethod
    def _expected_response(status_code):
        """Expected response mock."""
        response = MagicMock()
        response.content = '{"napps": []}'.encode()
        response.status_code = status_code
        return response

    @patch('requests.get')
    def test_get_napps(self, mock_request):
        """Test get_napps method."""
        mock_request.return_value = self._expected_response(200)

        self.napps_client.get_napps()

        mock_request.assert_called_with('endpoint/napps/', json=[])

    @patch('requests.get')
    def test_get_napp(self, mock_request):
        """Test get_napp method."""
        mock_request.return_value = self._expected_response(200)

        self.napps_client.get_napp('username', 'name')

        endpoint = 'endpoint/napps/username/name/'
        mock_request.assert_called_with(endpoint, json=[])

    @patch('requests.get')
    def test_reload_napps__all(self, mock_request):
        """Test reload_napps method to all napps."""
        mock_request.return_value = self._expected_response(200)

        self.napps_client.reload_napps()

        endpoint = 'endpoint/api/kytos/core/reload/all'
        mock_request.assert_called_with(endpoint, json=[])

    @patch('requests.get')
    def test_reload_napps__any(self, mock_request):
        """Test reload_napps method to any napp."""
        mock_request.return_value = self._expected_response(200)

        napps = [('user', 'napp', 'version')]
        self.napps_client.reload_napps(napps)

        endpoint = 'endpoint/api/kytos/core/reload/user/napp'
        mock_request.assert_called_with(endpoint, json=[])

    @patch('requests.post')
    @patch('requests.get')
    @patch('configparser.ConfigParser.set')
    @patch('configparser.ConfigParser.get', return_value='value')
    @patch('configparser.ConfigParser.has_option', return_value=False)
    @patch('kytos.utils.decorators.getpass', return_value='password')
    @patch('builtins.input', return_value='username')
    def test_upload_napp(self, *args):
        """Test upload_napp method."""
        (_, _, _, _, _, mock_get, mock_post) = args
        mock_get.return_value = self._expected_response(201)
        mock_post.return_value = self._expected_response(201)

        metadata = MagicMock()
        self.napps_client.upload_napp(metadata, 'package')

        mock_post.assert_called_with('value/napps/', data=metadata,
                                     files={'file': 'package'})

    @patch('requests.delete')
    @patch('requests.get')
    @patch('configparser.ConfigParser.set')
    @patch('configparser.ConfigParser.get', return_value='value')
    @patch('configparser.ConfigParser.has_option', return_value=False)
    @patch('kytos.utils.decorators.getpass', return_value='password')
    @patch('builtins.input', return_value='username')
    def test_delete(self, *args):
        """Test delete method."""
        (_, _, _, _, _, mock_get, mock_delete) = args
        mock_get.return_value = self._expected_response(201)
        mock_delete.return_value = self._expected_response(201)

        self.napps_client.delete('user', 'napp')

        endpoint = 'value/napps/user/napp/'
        token = self.napps_client._config.get('auth', 'token')
        mock_delete.assert_called_with(endpoint, json={'token': token})


class TestUsersClient(unittest.TestCase):
    """Test the class UsersClient."""

    def setUp(self):
        """Execute steps before each tests."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = '{}.kytosrc'.format(tmp_dir)
            kytos_config = KytosConfig(config_file)

        self.users_client = UsersClient()
        self.users_client._config = kytos_config.config
        self.users_client._config.set('napps', 'api', 'endpoint')

    @patch('requests.post')
    def test_register(self, mock_request):
        """Test register method."""
        user_dict = MagicMock()
        self.users_client.register(user_dict)

        mock_request.assert_called_with('endpoint/users/', json=user_dict)
