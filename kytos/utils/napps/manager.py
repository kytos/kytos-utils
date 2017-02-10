"""Manage Network Application files."""
import logging
import shutil
from pathlib import Path

log = logging.getLogger(__name__)


class NAppsManager:
    """Deal with NApps at filesystem level and ask Kyco to (un)load NApps."""

    def __init__(self, controller=None, install_path=None, enabled_path=None):
        """If controller is not informed, the necessary paths must be.

        If ``controller`` is available, NApps will be (un)loaded at runtime and
        you don't need to inform the paths. Otherwise, you should inform the
        required paths for the methods called.

        Args:
            controller (kyco.Controller): Controller to (un)load NApps.
            install_path (str): Folder where NApps should be installed. If
                None, use the controller's configuration.
            enabled_path (str): Folder where enabled NApps are stored. If None,
                use the controller's configuration.
        """
        self.controller = controller
        if controller is not None:
            if install_path is None:
                install_path = controller.options.installed_napps
            if enabled_path is None:
                enabled_path = controller.options.napps
        self._installed = Path(install_path) if install_path else None
        self._enabled = Path(enabled_path) if enabled_path else None

    @staticmethod
    def _get_napps(napps_dir):
        """List of (author, napp_name) found in ``napps_dir``."""
        jsons = napps_dir.glob('*/*/kytos.json')
        return sorted(j.parts[-3:-1] for j in jsons)

    def get_enabled(self):
        """Sorted list of (author, napp_name) of enabled napps."""
        return self._get_napps(self._enabled)

    def get_installed(self):
        """Sorted list of (author, napp_name) of installed napps."""
        return self._get_napps(self._installed)

    def is_installed(self, author, napp_name):
        """Whether a NApp is installed."""
        return (author, napp_name) in self.get_installed()

    def get_disabled(self):
        """Sorted list of (author, napp_name) of disabled napps.

        The difference of installed and enabled.
        """
        installed = set(self.get_installed())
        enabled = set(self.get_enabled())
        return sorted(installed - enabled)

    def disable(self, author, napp_name):
        """Disable a NApp by removing its symbolic link."""
        enabled = self._enabled / author / napp_name
        try:
            enabled.unlink()
            self._clean_author(enabled.parent)
            print(enabled.parents[1])
            log.info('Disabled NApp %s/%s', author, napp_name)

            if self.controller is not None:
                self.controller.unload_napp(author, napp_name)
        except FileNotFoundError:
            log.warning('NApp %s/%s was not enabled', author, napp_name)

    def enable(self, author, napp_name):
        """Enable a NApp by creating the a symbolic link."""
        enabled = self._enabled / author / napp_name
        installed = self._installed / author / napp_name

        if not installed.is_dir():
            log.error('Install NApp %s/%s first', author, napp_name)
        elif enabled.exists():
            log.warning('NApp %s/%s was already enabled', author, napp_name)
        else:
            # Make sure the enabled author/__init__.py exists.
            author = enabled.parent
            author.mkdir(exist_ok=True)
            init = author / '__init__.py'
            try:
                init.touch()
            except FileExistsError:
                pass  # No need to change the file modification time

            # Create symlink
            enabled.symlink_to(installed)

            log.info('Enabled NApp %s/%s', author, napp_name)
            if self.controller is not None:
                self.controller.load_napp(author, napp_name)

    def _clean_author(self, author_dir):
        """Remove author folder if there's no NApps inside."""
        if not self._get_napps(author_dir):
            shutil.rmtree(author_dir)
