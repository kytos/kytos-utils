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

    @patch('requests.get')
    @patch('kytos.utils.config.KytosConfig.save_token')
    @patch('builtins.input', return_value='username')
    @patch('kytos.utils.decorators.getpass', return_value='password')
    def test_authenticate_success_and_fail(self, *args):
        """Test authenticate method.

        This test check the fail and success cases. At the first, the 401
        status code will cause a fail and after that the 201 status code will
        test the success case. The authenticate has to be called twice, once
        the test `test_authenticate_success_and_fail` calls `authenticate`
        the first time, and the fail case will cause the second call."""
        (_, _, _, mock_requests_get) = args
        mock_requests_get.side_effect = [self._expected_response(401),
                                         self._expected_response(201)]

        authenticate = self.kytos_auth.authenticate
        self.kytos_auth.authenticate = MagicMock(side_effect=authenticate)

        self.kytos_auth.authenticate()

        call_count = self.kytos_auth.authenticate.call_count

        self.assertEqual(call_count, 2)
