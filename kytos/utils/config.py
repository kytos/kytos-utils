"""Kytos utils configuration."""
# This file is part of kytos-utils.
#
# Copyright (c) 2016 Kytos Team
#
# Authors:
#    Beraldo Leal <beraldo AT ncc DOT unesp DOT br>

import logging
import os
from configparser import ConfigParser

log = logging.getLogger(__name__)


class KytosConfig():
    """Kytos Configs.

    Read the config file for kytos utils and/or request data for the user in
    order to get the correct paths and links.
    """

    def __init__(self, config_file='~/.kytosrc'):
        """Init method.

        Receive the confi_file as argument.
        """
        self.config_file = os.path.expanduser(config_file)
        self.debug = False
        if self.debug:
            log.setLevel(logging.DEBUG)

        # allow_no_value=True is used to keep the comments on the config file.
        self.config = ConfigParser(allow_no_value=True)

        # Parse the config file. If no config file was found, then create some
        # default sections on the config variable.
        self.config.read(self.config_file)
        self.check_sections(self.config)

        self.set_env_or_defaults()

        if not os.path.exists(self.config_file):
            log.warning("Config file %s not found.", self.config_file)
            log.warning("Creating a new empty config file.")
            with open(self.config_file, 'w') as output_file:
                os.chmod(self.config_file, 0o0600)
                self.config.write(output_file)

    def log_configs(self):
        """Log the read configs if debug is enabled."""
        for sec in self.config.sections():
            log.debug('   %s: %s', sec, self.config.options(sec))

    def set_env_or_defaults(self):
        """Read some environment variables and set them on the config.

        If no environment variable is found and the config section/key is
        empty, then set some default values.
        """
        napps_api = os.environ.get('NAPPS_API_URI')
        napps_repo = os.environ.get('NAPPS_REPO_URI')
        user = os.environ.get('NAPPS_USER')
        token = os.environ.get('NAPPS_TOKEN')
        napps_path = os.environ.get('NAPPS_PATH')

        self.config.set('global', 'debug', str(self.debug))

        if user is not None:
            self.config.set('auth', 'user', user)

        if token is not None:
            self.config.set('auth', 'token', token)

        if napps_api is not None:
            self.config.set('napps', 'api', napps_api)
        elif not self.config.has_option('napps', 'api'):
            self.config.set('napps', 'api', 'https://napps.kytos.io/api/')

        if napps_repo is not None:
            self.config.set('napps', 'repo', napps_repo)
        elif not self.config.has_option('napps', 'repo'):
            self.config.set('napps', 'repo', 'https://napps.kytos.io/repo/')

        self._set_napps_path(napps_path)

    def _set_napps_path(self, napps_path):
        """Set paths if NAPPS_PATH is given or if not found in config."""
        if napps_path or not self.config.has_option('napps', 'enabled_path'):
            if not napps_path:  # default paths
                base = os.environ.get('VIRTUAL_ENV') or '/'
                napps_path = os.path.join(base, 'var', 'lib', 'kytos', 'napps')
            self.config.set('napps', 'enabled_path', napps_path)
            self.config.set('napps', 'installed_path',
                            os.path.join(napps_path, '.installed'))

    @staticmethod
    def check_sections(config):
        """Create a empty config file."""
        default_sections = ['global', 'auth', 'napps']
        for section in default_sections:
            if not config.has_section(section):
                config.add_section(section)

    def save_token(self, user, token):
        """Save the token on the config file."""
        self.config.set('auth', 'user', user)
        self.config.set('auth', 'token', token)
        # allow_no_value=True is used to keep the comments on the config file.
        new_config = ConfigParser(allow_no_value=True)

        # Parse the config file. If no config file was found, then create some
        # default sections on the config variable.
        new_config.read(self.config_file)
        self.check_sections(new_config)

        new_config.set('auth', 'user', user)
        new_config.set('auth', 'token', token)
        filename = os.path.expanduser(self.config_file)
        with open(filename, 'w') as out_file:
            os.chmod(filename, 0o0600)
            new_config.write(out_file)

    def clear_token(self):
        """Clear Token information on config file."""
        # allow_no_value=True is used to keep the comments on the config file.
        new_config = ConfigParser(allow_no_value=True)

        # Parse the config file. If no config file was found, then create some
        # default sections on the config variable.
        new_config.read(self.config_file)
        self.check_sections(new_config)

        new_config.remove_option('auth', 'user')
        new_config.remove_option('auth', 'token')
        filename = os.path.expanduser(self.config_file)
        with open(filename, 'w') as out_file:
            os.chmod(filename, 0o0600)
            new_config.write(out_file)
