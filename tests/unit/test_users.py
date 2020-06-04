"""kytos.utils.users tests."""
import unittest
from unittest.mock import patch

from kytos.utils.users import UsersManager


class TestUsersManager(unittest.TestCase):
    """Test the class UsersManager."""

    def setUp(self):
        """Execute steps before each tests."""
        self.user_manager = UsersManager()

    @patch('kytos.utils.client.UsersClient.register')
    @patch('kytos.utils.users.UsersManager.ask_question')
    def test_register(self, *args):
        """Test register method."""
        (mock_ask_question, mock_register) = args
        self.user_manager.register()

        self.assertEqual(mock_ask_question.call_count, 9)
        mock_register.assert_called()

    @patch('builtins.input', return_value='input')
    def test_ask_question(self, _):
        """Test ask_question method."""
        input_value = self.user_manager.ask_question('field')

        self.assertEqual(input_value, 'input')

    @patch('kytos.utils.users.getpass', return_value='password')
    def test_ask_question__password(self, _):
        """Test ask_question method with password."""
        input_value = self.user_manager.ask_question('field', password=True)

        self.assertEqual(input_value, 'password')
