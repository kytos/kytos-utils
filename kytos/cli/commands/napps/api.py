"""Translate cli commands to non-cli code."""
import os
import re

from kytos.utils.config import KytosConfig
from kytos.utils.napps import NAppsManager


class NAppsAPI:
    """An API for the command-line interface.

    Use the config file only for required options. Static methods are called
    by the parser and they instantiate an object of this class to fulfill the
    request.
    """

    @classmethod
    def disable(cls, args):
        """Disable subcommand."""
        napps = args['<napp>']
        mgr = cls.get_napps_manager()
        for napp in napps:
            mgr.disable(*napp)

    @classmethod
    def enable(cls, args):
        """Enable subcommand."""
        napps = args['<napp>']
        mgr = cls.get_napps_manager()
        for napp in napps:
            mgr.enable(*napp)

    @staticmethod
    def get_napps_manager():
        """Instance of NAppsManager with settings from config file."""
        config = KytosConfig().config['napps']
        return NAppsManager(install_path=config['installed_path'],
                            enabled_path=config['enabled_path'])

    @classmethod
    def create(cls, args):
        """Bootstrap a basic NApp structure on the current folder."""
        NAppsManager.create_napp()

    @classmethod
    def uninstall(cls, args):
        """Uninstall and delete NApps.

        For local installations, do not delete code outside install_path and
        enabled_path.
        """
        napps = args['<napp>']
        mgr = cls.get_napps_manager()
        for napp in napps:
            mgr.uninstall(*napp)

    @classmethod
    def search(cls, args):
        """Search for NApps in NApps server matching a pattern."""
        safe_shell_pat = re.escape(args['<pattern>']).replace(r'\*', '.*')
        pat_str = '.*{}.*'.format(safe_shell_pat)
        pattern = re.compile(pat_str, re.IGNORECASE)
        remote_json = NAppsManager.search(pattern)

        mgr = cls.get_napps_manager()
        enabled = mgr.get_enabled()
        disabled = mgr.get_disabled()
        remote = (((n['author'], n['name']), n['description'])
                  for n in remote_json)

        napps = []
        for napp, desc in remote:
            if napp in enabled:
                status = 'ie'
            elif napp in disabled:
                status = 'i-'
            else:
                status = '--'
            status = '[{}]'.format(status)
            name = '{}/{}'.format(*napp)
            napps.append((status, name, desc))

        cls.print_napps(napps)

    @classmethod
    def list(cls, args):
        """List all installed NApps and inform whether they are installed."""
        mgr = cls.get_napps_manager()

        # Add status
        napps = [napp + ('[ie]',) for napp in mgr.get_enabled()]
        napps += [napp + ('[i-]',) for napp in mgr.get_disabled()]

        # Sort, add description and reorder coloumns
        napps.sort()
        napps = [(s, '{}/{}'.format(u, n), mgr.get_description(u, n))
                 for u, n, s in napps]

        cls.print_napps(napps)

    @staticmethod
    def print_napps(napps):
        """Print status, name and description."""
        if not napps:
            print('No NApps found.')
            return

        stat_w = 6  # We already know the size of Status col
        name_w = max(len(n[1]) for n in napps)
        desc_w = max(len(n[2]) for n in napps)
        term_w = os.popen('stty size', 'r').read().split()[1]
        remaining = int(term_w) - stat_w - name_w - 6
        desc_w = min(desc_w, remaining)
        widths = (stat_w, name_w, desc_w)

        header = '\n{:^%d} | {:^%d} | {:^%d}' % widths
        row = '{:^%d} | {:<%d} | {:<%d}' % widths
        print(header.format('Status', 'NApp', 'Description'))
        print('=+='.join('=' * w for w in widths))
        for user, name, desc in napps:
            desc = (desc[:desc_w-3] + '...') if len(desc) > desc_w else desc
            print(row.format(user, name, desc))

        print('\nStatus: (i)nstalled, (e)nabled\n')
