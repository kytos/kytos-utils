"""kytos.utils.decorators tests."""
import unittest
from unittest.mock import MagicMock, patch

from kytos.utils.config import KytosConfig
from kytos.utils.decorators import kytos_auth


class TestKytosAuth(unittest.TestCase):
    """Test the decorator kytos_auth."""

    def setUp(self):
        """Execute steps before each tests."""
        self.kytos_auth = kytos_auth(MagicMock())
        self.kytos_auth.__get__(MagicMock(), MagicMock())

        config = KytosConfig('/tmp/.kytosrc').config
        config.set('auth', 'user', 'username')
        config.set('auth', 'token', 'hash')
        self.kytos_auth.config = config

    @staticmethod
    def _expected_response(status_code):
        """Expected response mock."""
        response = MagicMock()
        response.json.return_value = {"hash": "hash"}
        response.status_code = status_code
        return response

    @patch('requests.get')
    @patch('configparser.ConfigParser.set')
    @patch('configparser.ConfigParser.get', return_value='value')
    @patch('configparser.ConfigParser.has_option', return_value=False)
    @patch('kytos.utils.decorators.getpass', return_value='password')
    @patch('builtins.input', return_value='username')
    def test__call__(self, *args):
        """Test __call__ method."""
        (_, _, _, _, mock_set, mock_requests_get) = args
        mock_requests_get.return_value = self._expected_response(201)

        self.kytos_auth.__call__()

        mock_set.assert_any_call('auth', 'user', 'username')
        mock_set.assert_any_call('auth', 'token', 'hash')

    @patch('sys.exit')
    @patch('requests.get')
    @patch('kytos.utils.config.KytosConfig.save_token')
    @patch('kytos.utils.decorators.getpass', return_value='password')
    def test_authenticate(self, *args):
        """Test authenticate method."""
        (_, mock_save_token, mock_requests_get, _) = args
        mock_requests_get.return_value = self._expected_response(401)

        try:
            self.kytos_auth.authenticate()
        except OSError:
            print("Handle unnecessary OSError")

        mock_save_token.assert_not_called()
