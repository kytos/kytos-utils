"""kytos.cli.commands.web.api.WebAPI tests."""
import unittest
from unittest.mock import patch

from kytos.cli.commands.web.api import WebAPI
from kytos.utils.config import KytosConfig


class TestWebAPI(unittest.TestCase):
    """Test the class WebAPI."""

    def setUp(self):
        """Execute steps before each tests."""
        self.web_api = WebAPI()

    @patch('requests.post')
    def test_update(self, mock_post):
        """Test update method."""
        args = {'<version>': 'ABC'}
        self.web_api.update(args)

        kytos_api = KytosConfig().config.get('kytos', 'api')
        url = f"{kytos_api}api/kytos/core/web/update/ABC"
        mock_post.assert_called_with(url)
