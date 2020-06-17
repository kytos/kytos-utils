"""kytos.cli.commands.users.api.UsersAPI tests."""
import unittest
from unittest.mock import patch

from kytos.cli.commands.users.api import UsersAPI


class TestUsersAPI(unittest.TestCase):
    """Test the class UsersAPI."""

    def setUp(self):
        """Execute steps before each tests."""
        self.users_api = UsersAPI()

    @patch('kytos.utils.users.UsersManager.register')
    def test_register(self, mock_register):
        """Test register method."""
        self.users_api.register(None)

        mock_register.assert_called()
