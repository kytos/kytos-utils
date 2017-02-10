"""Translate cli commands to non-cli code."""
from os import environ, path

from kytos.utils.config import Config
from kytos.utils.exceptions import KytosException
from kytos.utils.napps.manager import NAppsManager


class NAppsAPI:
    """An API for the command-line interface.

    Use the config file only for required options. Static methods are called
    by the parser and they instantiate an object of this class to fulfill the
    request.
    """

    @classmethod
    def disable(cls, args):
        """Disable subcommand."""
        obj = cls(args)
        obj.assert_napp()
        mgr = NAppsManager(enabled_path=obj.get_enabled_path())
        for napp in obj.napps:
            mgr.disable(*napp)

    @classmethod
    def enable(cls, args):
        """Enable subcommand."""
        obj = cls(args)
        obj.assert_napp()
        mgr = NAppsManager(install_path=obj.get_install_path(),
                           enabled_path=obj.get_enabled_path())
        for napp in obj.napps:
            mgr.enable(*napp)

    def __init__(self, args):
        """Require parsed arguments.

        Args:
            args (dict): Parsed arguments from cli.
        """
        self.napps = args['<napp>'] if '<napp>' in args else []
        self._config = Config('napps')

    def assert_napp(self):
        """Make sure that user provided at least one NApp in cli."""
        if not self.napps:
            raise KytosException("Missing NApps.")

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

    @classmethod
    def uninstall(cls, args):
        """Uninstall and delete NApps.

        For local installations, do not delete code outside install_path and
        enabled_path.
        """
        obj = cls(args)
        obj.assert_napp()
        mgr = NAppsManager(install_path=obj.get_install_path(),
                           enabled_path=obj.get_enabled_path())
        for napp in obj.napps:
            mgr.uninstall(*napp)

    @classmethod
    def list(cls, args):
        """List all installed NApps and inform whether they are installed."""
        obj = cls(args)
        mgr = NAppsManager(install_path=obj.get_install_path(),
                           enabled_path=obj.get_enabled_path())
        # Adding status
        napps = [napp + ('[IE]',) for napp in mgr.get_enabled()]
        napps += [napp + ('[ID]',) for napp in mgr.get_disabled()]
        napps.sort()

        # After sorting, format NApp name and move status to the first position
        napps = [(n[2], n[0] + '/' + n[1]) for n in napps]
        titles = 'Status', 'NApp'

        # Calculate maximum width of columns to be printed
        widths = [max(len(napp[col]) for napp in napps) for col in range(2)]
        widths = [max(w, len(t)) for w, t in zip(widths, titles)]
        widths = tuple(widths)

        header = '\n{:^%d} {:^%d}' % widths
        sep = '{:=^%d} {:=^%d}' % widths
        row = '{:^%d} {}' % widths[:-1]

        print(header.format(*titles))
        print(sep.format('', ''))
        for napp in napps:
            print(row.format(*napp))

        print('\nStatus: (I)nstalled, (E)nabled, (D)isabled\n')
