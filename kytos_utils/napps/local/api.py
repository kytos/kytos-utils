"""Translate cli commands to non-cli code."""
from os import environ, path

from kytos_utils.config import Config
from kytos_utils.napps.local.manager import NAppsManager


class NAppsAPI:
    """Receive arguments from cli and execute the desired commands.

    Use the config file only for required options. Static methods are called
    by the parser and they instantiate an object of this class to fulfill the
    request.
    """

    @classmethod
    def disable(cls, args):
        """Disable subcommand."""
        obj = cls(args)
        enabled_path = obj.get_enabled_path()
        mgr = NAppsManager(enabled_path=enabled_path)
        mgr.disable(*obj.napp)

    @classmethod
    def enable(cls, args):
        """Enable subcommand."""
        obj = cls(args)
        i_path = obj.get_install_path()
        e_path = obj.get_enabled_path()
        mgr = NAppsManager(install_path=i_path, enabled_path=e_path)
        mgr.enable(*obj.napp)

    def __init__(self, args):
        """Require parsed arguments.

        Args:
            args (argparse.Namespace): Parsed arguments by :mod:`..argparser`.
        """
        self.napp = self.parse_napp(args)
        self._config = Config('napps')

    @staticmethod
    def parse_napp(args):
        """Return author and name from the ``NApp`` value or None if not found.

        The expected format of a NApp is napp_author/napp_name.

        Args:
            args (argparse.Namespace): Parsed arguments by :mod:`..argparser`.

        Return:
            str: Author name.
            str: NApp name.

        Raises:
            ValueError: If it form is different from _author/name_.
        """
        if 'NApp' not in args:
            return None
        napp = args.NApp.split('/')
        if len(napp) != 2 or len(napp[0]) == 0 or len(napp[1]) == 0:
            raise ValueError('"{}" is not a valid NApp name. A NApp is of the '
                             'form author/napp_name.'.format(args.NApp))
        return napp

    def get_install_path(self):
        """Get install_path from config. Create if necessary."""
        def default():
            """Append "/.installed" to the enabled_path."""
            # Set the enabled_path for interpolation
            self.get_enabled_path()
            return '%(enabled_path)s/.installed'

        return self._config.setdefault('install_path', default, warn=True)

    def get_enabled_path(self):
        """Get enabled_path from config. Create if necessary."""
        def default():
            """Based on kyco-core-napps/setup.py."""
            base = environ['VIRTUAL_ENV'] if 'VIRTUAL_ENV' in environ else '/'
            return path.join(base, 'var', 'lib', 'kytos', 'napps')

        return self._config.setdefault('enabled_path', default, warn=True)
