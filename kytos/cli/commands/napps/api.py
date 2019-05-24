"""Translate cli commands to non-cli code."""
import json
import logging
import os
import re
from urllib.error import HTTPError, URLError

import requests

from kytos.utils.exceptions import KytosException
from kytos.utils.napps import NAppsManager

LOG = logging.getLogger(__name__)


class NAppsAPI:
    """An API for the command-line interface.

    Use the config file only for required options. Static methods are called
    by the parser and they instantiate an object of this class to fulfill the
    request.
    """

    @classmethod
    def disable(cls, args):
        """Disable subcommand."""
        mgr = NAppsManager()

        if args['all']:
            napps = mgr.get_enabled()
        else:
            napps = args['<napp>']

        for napp in napps:
            mgr.set_napp(*napp)
            LOG.info('NApp %s:', mgr.napp_id)
            cls.disable_napp(mgr)

    @staticmethod
    def disable_napp(mgr):
        """Disable a NApp."""
        if mgr.is_enabled():
            LOG.info('  Disabling...')
            mgr.disable()
            LOG.info('  Disabled.')
        else:
            LOG.error("  NApp isn't enabled.")

    @classmethod
    def enable(cls, args):
        """Enable subcommand."""
        mgr = NAppsManager()

        if args['all']:
            napps = mgr.get_disabled()
        else:
            napps = args['<napp>']

        cls.enable_napps(napps)

    @classmethod
    def enable_napp(cls, mgr):
        """Install one NApp using NAppManager object."""
        try:
            if not mgr.is_enabled():
                LOG.info('    Enabling...')
                mgr.enable()

            # Check if NApp is enabled
            if mgr.is_enabled():
                LOG.info('    Enabled.')
            else:
                LOG.error('    Error enabling NApp.')
        except (FileNotFoundError, PermissionError) as exception:
            LOG.error('  %s', exception)

    @classmethod
    def enable_napps(cls, napps):
        """Enable a list of NApps.

        Args:
            napps (list): List of NApps.
        """
        mgr = NAppsManager()
        for napp in napps:
            mgr.set_napp(*napp)
            LOG.info('NApp %s:', mgr.napp_id)
            cls.enable_napp(mgr)

    @classmethod
    def create(cls, args):  # pylint: disable=unused-argument
        """Bootstrap a basic NApp structure on the current folder."""
        NAppsManager.create_napp(meta_package=args.get('--meta', False))

    @classmethod
    def upload(cls, args):  # pylint: disable=unused-argument
        """Upload the NApp to the NApps server.

        Create the NApp package and upload it to the NApp server.
        """
        try:
            NAppsManager().upload()
        except FileNotFoundError as err:
            LOG.error("Couldn't find %s in current directory.", err.filename)

    @classmethod
    def uninstall(cls, args):
        """Uninstall and delete NApps.

        For local installations, do not delete code outside install_path and
        enabled_path.
        """
        mgr = NAppsManager()
        for napp in args['<napp>']:
            mgr.set_napp(*napp)
            LOG.info('NApp %s:', mgr.napp_id)
            if mgr.is_installed():
                if mgr.is_enabled():
                    cls.disable_napp(mgr)
                LOG.info('  Uninstalling...')
                mgr.remote_uninstall()
                LOG.info('  Uninstalled.')
            else:
                LOG.error("  NApp isn't installed.")

    @classmethod
    def install(cls, args):
        """Install local or remote NApps."""
        cls.install_napps(args['<napp>'])

    @classmethod
    def install_napps(cls, napps):
        """Install local or remote NApps.

        This method is recursive, it will install each napps and your
        dependencies.
        """
        mgr = NAppsManager()
        for napp in napps:
            mgr.set_napp(*napp)
            LOG.info('  NApp %s:', mgr.napp_id)

            try:
                if not mgr.is_installed():
                    # Try to install all NApps, even if
                    # some of them fail.
                    cls.install_napp(mgr)

                    # Enable the NApp
                    if not mgr.is_enabled():
                        cls.enable_napp(mgr)
                        napp_dependencies = mgr.dependencies()
                        if napp_dependencies:
                            LOG.info('Installing Dependencies:')
                            cls.install_napps(napp_dependencies)
                    else:
                        LOG.info('    Enabled.')
                else:
                    LOG.warning('  Napp already installed.')
            except KytosException:
                LOG.error('Error installing NApp.')
                continue

    @classmethod
    def install_napp(cls, mgr):
        """Install a NApp.

        Raises:
            KytosException: If a NApp hasn't been found.

        """
        try:
            LOG.info('    Searching local NApp...')
            mgr.install_local()
            LOG.info('    Found and installed.')
        except FileNotFoundError:
            LOG.info('    Not found. Downloading from NApps Server...')
            try:
                mgr.remote_install()
                LOG.info('    Downloaded and installed.')
                return
            except HTTPError as exception:
                if exception.code == 404:
                    LOG.error('    NApp not found.')
                else:
                    LOG.error('    NApps Server error: %s', exception)
            except URLError as exception:
                LOG.error('    NApps Server error: %s', str(exception.reason))
            raise KytosException("NApp not found.")

    @classmethod
    def search(cls, args):
        """Search for NApps in NApps server matching a pattern."""
        safe_shell_pat = re.escape(args['<pattern>']).replace(r'\*', '.*')
        pat_str = '.*{}.*'.format(safe_shell_pat)
        pattern = re.compile(pat_str, re.IGNORECASE)
        remote_json = NAppsManager.search(pattern)
        remote = set()
        for napp in remote_json:
            # WARNING: This will be changed in future versions, when 'author'
            # will be removed.
            username = napp.get('username', napp.get('author'))
            remote.add(((username, napp.get('name')), napp.get('description')))

        cls._print_napps(remote)

    @classmethod
    def _print_napps(cls, napp_list):
        """Format the NApp list to be printed."""
        mgr = NAppsManager()
        enabled = mgr.get_enabled()
        installed = mgr.get_installed()
        napps = []
        for napp, desc in sorted(napp_list):
            status = 'i' if napp in installed else '-'
            status += 'e' if napp in enabled else '-'
            status = '[{}]'.format(status)
            name = '{}/{}'.format(*napp)
            napps.append((status, name, desc))
        cls.print_napps(napps)

    @classmethod
    def list(cls, args):  # pylint: disable=unused-argument
        """List all installed NApps and inform whether they are enabled."""
        mgr = NAppsManager()

        # Add status
        napps = [napp + ('[ie]',) for napp in mgr.get_enabled()]
        napps += [napp + ('[i-]',) for napp in mgr.get_disabled()]

        # Sort, add description and reorder columns
        napps.sort()
        napps_ordered = []
        for user, name, status in napps:
            description = mgr.get_description(user, name)
            version = mgr.get_version(user, name)
            napp_id = f'{user}/{name}'
            if version:
                napp_id += f':{version}'

            napps_ordered.append((status, napp_id, description))

        cls.print_napps(napps_ordered)

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
        remaining = max(0, int(term_w) - stat_w - name_w - 6)
        desc_w = min(desc_w, remaining)
        widths = (stat_w, name_w, desc_w)

        header = '\n{:^%d} | {:^%d} | {:^%d}' % widths
        row = '{:^%d} | {:<%d} | {:<%d}' % widths
        print(header.format('Status', 'NApp ID', 'Description'))
        print('=+='.join('=' * w for w in widths))
        for user, name, desc in napps:
            desc = (desc[:desc_w - 3] + '...') if len(desc) > desc_w else desc
            print(row.format(user, name, desc))

        print('\nStatus: (i)nstalled, (e)nabled\n')

    @staticmethod
    def delete(args):
        """Delete NApps from server."""
        mgr = NAppsManager()
        for napp in args['<napp>']:
            mgr.set_napp(*napp)
            LOG.info('Deleting NApp %s from server...', mgr.napp_id)
            try:
                mgr.delete()
                LOG.info('  Deleted.')
            except requests.HTTPError as exception:
                if exception.response.status_code == 405:
                    LOG.error('Delete Napp is not allowed yet.')
                else:
                    msg = json.loads(exception.response.content)
                    LOG.error('  Server error: %s - ', msg['error'])

    @classmethod
    def prepare(cls, args):  # pylint: disable=unused-argument
        """Create OpenAPI v3.0 spec skeleton."""
        mgr = NAppsManager()
        mgr.prepare()

    @classmethod
    def reload(cls, args):
        """Reload NApps code."""
        LOG.info('Reloading NApps...')
        mgr = NAppsManager()

        try:
            if args['all']:
                mgr.reload(None)
            else:
                napps = args['<napp>']
                mgr.reload(napps)

            LOG.info('\tReloaded.')
        except requests.HTTPError as exception:
            if exception.response.status_code != 200:
                msg = json.loads(exception.response.content)
                LOG.error('\tServer error: %s - ', msg['error'])
