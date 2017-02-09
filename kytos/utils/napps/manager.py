"""Manage Network Application files."""
import logging
import os
from os import listdir, path

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
        self._installed = install_path
        self._enabled = enabled_path

        if controller is not None:
            if install_path is None:
                self._installed = controller.options.installed_napps
            if enabled_path is None:
                self._enabled = controller.options.napps

    @staticmethod
    def _get_napps(napps_dir):
        """List of (author, napp_name) found in ``napps_dir``."""
        napps = []
        ignored_paths = set(['.installed', '__pycache__', '__init__.py'])
        for author in set(listdir(napps_dir)) - ignored_paths:
            author_dir = path.join(napps_dir, author)
            for napp_name in set(listdir(author_dir)) - ignored_paths:
                napps.append((author, napp_name))
        return sorted(napps)

    def get_enabled(self):
        """Sorted list of (author, napp_name) of enabled napps."""
        return self._get_napps(self._enabled)

    def get_installed(self):
        """Sorted list of (author, napp_name) of installed napps."""
        return self._get_napps(self._installed)

    def get_disabled(self):
        """Sorted list of (author, napp_name) of disabled napps.

        The difference of installed and enabled.
        """
        installed = set(self.get_installed())
        enabled = set(self.get_enabled())
        disabled = set(installed) - set(enabled)
        return sorted(disabled)

    def disable(self, author, napp_name):
        """Disable a NApp by removing its symbolic link."""
        napp_sym_path = path.join(self._enabled, author, napp_name)

        try:
            os.remove(napp_sym_path)
            log.info('Disabled NApp %s/%s', author, napp_name)
            if self.controller is not None:
                self.controller.unload_napp(author, napp_name)
        except FileNotFoundError:
            log.warning('NApp %s/%s was already disabled', author, napp_name)

    def enable(self, author, napp_name):
        """Enable a NApp by creating the a symbolic link."""
        napp_abs_path = path.join(self._installed, author, napp_name)
        napp_sym_path = path.join(self._enabled, author, napp_name)

        if not path.isdir(napp_abs_path):
            log.error('You should install NApp %s/%s first', author, napp_name)
        elif not path.exists(napp_sym_path):
            os.symlink(napp_abs_path, napp_sym_path)
            log.info('Enabled NApp %s/%s', author, napp_name)
            if self.controller is not None:
                self.controller.load_napp(author, napp_name)
        else:
            log.warning('NApp %s/%s was already enabled', author, napp_name)
