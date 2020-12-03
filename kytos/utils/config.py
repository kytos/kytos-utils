"""Kytos utils configuration."""
# This file is part of kytos-utils.
#
# Copyright (c) 2016 Kytos Team
#
# Authors:
#    Beraldo Leal <beraldo AT ncc DOT unesp DOT br>

import json
import logging
import os
import re
import shutil
from collections import namedtuple
from configparser import ConfigParser
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

LOG = logging.getLogger(__name__)


def create_skel_dir():
    """Install data_files in the /etc directory."""
    base_env = Path(os.environ.get('VIRTUAL_ENV', '/'))
    etc_kytos = base_env / 'etc' / 'kytos'

    # kytos-utils/kytos/utils/config.py -> kytos-utils/kytos
    parent_dir = Path(__file__).resolve().parent.parent

    if not etc_kytos.exists():
        os.makedirs(etc_kytos)

    src = parent_dir / 'templates' / 'skel'
    dst = etc_kytos / 'skel'

    if dst.exists():
        if not next(dst.iterdir(), None):
            # Path already exists but it's empty, so we'll populate it
            # We remove it first to avoid an exception from copytree
            dst.rmdir()
            shutil.copytree(str(src), str(dst))
    else:
        shutil.copytree(str(src), str(dst))


class KytosConfig():
    """Kytos Configs.

    Read the config file for kytos utils and/or request data for the user in
    order to get the correct paths and links.
    """

    def __init__(self, config_file='~/.kytosrc'):
        """Init method.

        Receive the config_file as argument.
        """
        create_skel_dir()
        self.config_file = os.path.expanduser(config_file)
        self.debug = False
        if self.debug:
            LOG.setLevel(logging.DEBUG)

        # allow_no_value=True is used to keep the comments on the config file.
        self.config = ConfigParser(allow_no_value=True)

        # Parse the config file. If no config file was found, then create some
        # default sections on the config variable.
        self.config.read(self.config_file)
        self.check_sections(self.config)

        self.set_env_or_defaults()

        if not os.path.exists(self.config_file):
            LOG.warning("Config file %s not found.", self.config_file)
            LOG.warning("Creating a new empty config file.")
            with open(self.config_file, 'w') as output_file:
                os.chmod(self.config_file, 0o0600)
                self.config.write(output_file)

    def log_configs(self):
        """Log the read configs if debug is enabled."""
        for sec in self.config.sections():
            LOG.debug('   %s: %s', sec, self.config.options(sec))

    def set_env_or_defaults(self):
        """Read some environment variables and set them on the config.

        If no environment variable is found and the config section/key is
        empty, then set some default values.
        """
        option = namedtuple('Option', ['section', 'name', 'env_var',
                                       'default_value'])

        options = [option('auth', 'user', 'NAPPS_USER', None),
                   option('auth', 'token', 'NAPPS_TOKEN', None),
                   option('napps', 'api', 'NAPPS_API_URI',
                          'https://napps.kytos.io/api/'),
                   option('napps', 'repo', 'NAPPS_REPO_URI',
                          'https://napps.kytos.io/repo'),
                   option('kytos', 'api', 'KYTOS_API',
                          'http://localhost:8181/')]

        for option in options:
            if not self.config.has_option(option.section, option.name):
                env_value = os.environ.get(option.env_var,
                                           option.default_value)
                if env_value:
                    self.config.set(option.section, option.name, env_value)

        self.config.set('global', 'debug', str(self.debug))

    @staticmethod
    def check_sections(config):
        """Create a empty config file."""
        default_sections = ['global', 'auth', 'napps', 'kytos']
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

    @classmethod
    def get_metadata(cls):
        """Return kytos-utils metadata."""
        meta_path = ("%s/metadata.py" % os.path.dirname(__file__))
        meta_file = open(meta_path).read()
        metadata = dict(re.findall(r"(__[a-z]+__)\s*=\s*'([^']+)'", meta_file))
        return metadata

    @classmethod
    def get_remote_metadata(cls):
        """Return kytos metadata."""
        kytos_api = KytosConfig().config.get('kytos', 'api')
        meta_uri = kytos_api + 'api/kytos/core/metadata/'
        meta_file = urlopen(meta_uri).read()
        metadata = json.loads(meta_file)
        return metadata

    @classmethod
    def check_versions(cls):
        """Check if kytos and kytos-utils metadata are compatible."""
        try:
            kytos_metadata = cls.get_remote_metadata()
            kytos_version = kytos_metadata.get('__version__')
        except URLError as exc:
            LOG.debug('Couldn\'t connect to kytos server: %s', exc)
        else:
            kutils_metadata = cls.get_metadata()
            kutils_version = kutils_metadata.get('__version__')

            if kytos_version != kutils_version:
                logger = logging.getLogger()
                logger.warning('kytos (%s) and kytos utils (%s) versions '
                               'are not equal.', kytos_version, kutils_version)
