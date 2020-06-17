"""kytos.utils.config tests."""
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from kytos.utils.config import KytosConfig


class TestKytosConfig(unittest.TestCase):
    """Test the class KytosConfig."""

    def setUp(self):
        """Execute steps before each tests."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.config_file = '{}.kytosrc'.format(tmp_dir)
        self.kytos_config = KytosConfig(self.config_file)

    def test_clear_token(self):
        """Test clear_token method."""
        self.kytos_config.clear_token()

        config = KytosConfig(self.config_file).config
        has_token = config.has_option('auth', 'token')
        self.assertFalse(has_token)

    def test_save_token(self):
        """Test save_token method."""
        self.kytos_config.save_token('user', 'token')

        config = KytosConfig(self.config_file).config
        has_token = config.has_option('auth', 'token')
        self.assertTrue(has_token)

    @patch('builtins.open')
    @patch('kytos.utils.config.urlopen')
    @patch('kytos.utils.config.logging.RootLogger.warning')
    def test_check_versions__success(self, *args):
        """Test check_versions method to success case."""
        (mock_warning, mock_urlopen, mock_open) = args
        urlopen = MagicMock()
        urlopen.read.return_value = '{"__version__": "123"}'
        mock_urlopen.return_value = urlopen

        read_file = MagicMock()
        read_file.read.return_value = "__version__ = '123'"
        mock_open.return_value = read_file

        self.kytos_config.check_versions()

        mock_warning.assert_not_called()

    @patch('builtins.open')
    @patch('kytos.utils.config.urlopen')
    @patch('kytos.utils.config.logging.RootLogger.warning')
    def test_check_versions__error(self, *args):
        """Test check_versions method to error case."""
        (mock_warning, mock_urlopen, mock_open) = args
        urlopen = MagicMock()
        urlopen.read.return_value = '{"__version__": "123"}'
        mock_urlopen.return_value = urlopen

        read_file = MagicMock()
        read_file.read.return_value = "__version__ = '456'"
        mock_open.return_value = read_file

        self.kytos_config.check_versions()

        mock_warning.assert_called_once()
