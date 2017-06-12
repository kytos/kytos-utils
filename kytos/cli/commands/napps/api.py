"""Translate cli commands to non-cli code."""
import json
import logging
import os
import re
from urllib.error import HTTPError

import requests

from kytos.utils.napps import NAppsManager

log = logging.getLogger(__name__)


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
            log.info('NApp %s:', mgr.napp_id)
            cls.disable_napp(mgr)

    @staticmethod
    def disable_napp(mgr):
        """Disable a NApp."""
        if mgr.is_enabled():
            log.info('  Disabling...')
            mgr.disable()
        log.info('  Disabled.')

    @classmethod
    def enable(cls, args):
        """Enable subcommand."""
        mgr = NAppsManager()

        if args['all']:
            napps = mgr.get_disabled()
        else:
            napps = args['<napp>']

        for napp in napps:
            mgr.set_napp(*napp)
            log.info('NApp %s:', mgr.napp_id)
            cls.enable_napp(mgr)

    @staticmethod
    def enable_napp(mgr):
        """Install one NApp using NAppManager object."""
        try:
            if not mgr.is_enabled():
                log.info('  Enabling...')
                mgr.enable()
            log.info('  Enabled.')
        except (FileNotFoundError, PermissionError) as e:
            log.error('  %s', e)

    @classmethod
    def create(cls, args):
        """Bootstrap a basic NApp structure on the current folder."""
        NAppsManager.create_napp()

    @classmethod
    def upload(cls, args):
        """Upload the NApp to the NApps server.

        Create the NApp package and upload it to the NApp server.
        """
        try:
            NAppsManager().upload()
        except FileNotFoundError:
            log.error("Couldn't find kytos.json in current directory.")

    @classmethod
    def uninstall(cls, args):
        """Uninstall and delete NApps.

        For local installations, do not delete code outside install_path and
        enabled_path.
        """
        mgr = NAppsManager()
        for napp in args['<napp>']:
            mgr.set_napp(*napp)
            log.info('NApp %s:', mgr.napp_id)
            if mgr.is_installed():
                if mgr.is_enabled():
                    cls.disable_napp(mgr)
                log.info('  Uninstalling...')
                mgr.uninstall()
            log.info('  Uninstalled.')

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
            log.info('NApp %s:', mgr.napp_id)
            if not mgr.is_installed():
                cls.install_napp(mgr)
            else:
                log.info('  Installed.')
            napp_dependencies = mgr.dependencies()
            if napp_dependencies:
                log.info('Installing Dependencies:')
                cls.install_napps(napp_dependencies)

    @classmethod
    def install_napp(cls, mgr):
        """Install a NApp."""
        try:
            log.info('  Searching local NApp...')
            mgr.install_local()
            log.info('  Found and installed.')
            cls.enable_napp(mgr)
        except FileNotFoundError:
            log.info('  Not found. Downloading from NApps Server...')
            try:
                mgr.install_remote()
                log.info('  Downloaded and installed.')
                cls.enable_napp(mgr)
            except HTTPError as e:
                if e.code == 404:
                    log.error('  NApp not found.')
                else:
                    log.error('  NApps Server error: %s', e)

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
    def list(cls, args):
        """List all installed NApps and inform whether they are enabled."""
        mgr = NAppsManager()

        # Add status
        napps = [napp + ('[ie]',) for napp in mgr.get_enabled()]
        napps += [napp + ('[i-]',) for napp in mgr.get_disabled()]

        # Sort, add description and reorder coloumns
        napps.sort()
        napps_ordered = []
        for user, name, status in napps:
            napps_ordered.append((status, '{}/{}'.format(user, name),
                                  mgr.get_description(user, name)))

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
        remaining = int(term_w) - stat_w - name_w - 6
        desc_w = min(desc_w, remaining)
        widths = (stat_w, name_w, desc_w)

        header = '\n{:^%d} | {:^%d} | {:^%d}' % widths
        row = '{:^%d} | {:<%d} | {:<%d}' % widths
        print(header.format('Status', 'NApp ID', 'Description'))
        print('=+='.join('=' * w for w in widths))
        for user, name, desc in napps:
            desc = (desc[:desc_w-3] + '...') if len(desc) > desc_w else desc
            print(row.format(user, name, desc))

        print('\nStatus: (i)nstalled, (e)nabled\n')

    @staticmethod
    def delete(args):
        """Delete NApps from server."""
        mgr = NAppsManager()
        for napp in args['<napp>']:
            mgr.set_napp(*napp)
            log.info('Deleting NApp %s from server...', mgr.napp_id)
            try:
                mgr.delete()
                log.info('  Deleted.')
            except requests.HTTPError as e:
                if e.response.status_code == 405:
                    log.error('Delete Napp is not allowed yet.')
                else:
                    msg = json.loads(e.response.content)
                    log.error('  Server error: %s - ', msg['error'])
