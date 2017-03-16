"""Decorators for Kytos-utils."""
import logging
import os
import sys
from getpass import getpass

import requests
from kytos.utils.config import KytosConfig

log = logging.getLogger(__name__)


class kytos_auth:
    """Class to be used as decorator to require authentication."""

    def __init__(self, func):
        """Init method.

        Save the function on the func attribute and bootstrap a new config.
        """
        self.func = func
        self.config = KytosConfig().config

    def __call__(self, *args, **kwargs):
        """Code run when func is called."""
        if not (self.config.has_option('napps', 'api') and
                self.config.has_option('napps', 'repo')):
            uri = input("Enter the kytos napps server address: ")
            self.config.set('napps', 'api', os.path.join(uri, 'api', ''))
            self.config.set('napps', 'repo', os.path.join(uri, 'repo', ''))

        if not self.config.has_option('auth', 'user'):
            user = input("Enter the username: ")
            self.config.set('auth', 'user', user)
        else:
            user = self.config.get('auth', 'user')

        if not self.config.has_option('auth', 'token'):
            token = self.authenticate()
        else:
            token = self.config.get('auth', 'token')

        # pylint: disable=W0212
        self.obj._config.set('auth', 'user', user)
        # pylint: disable=W0212
        self.obj._config.set('auth', 'token', token)
        self.func.__call__(self.obj, *args, **kwargs)

    def __get__(self, instance, owner):
        """Deal with owner class."""
        # pylint: disable=W0201
        self.cls = owner
        # pylint: disable=W0201
        self.obj = instance

        return self.__call__

    def authenticate(self):
        """Check the user authentication."""
        endpoint = os.path.join(self.config.get('napps', 'api'), 'auth', '')
        username = self.config.get('auth', 'user')
        password = getpass("Enter the password for {}: ".format(username))
        response = requests.get(endpoint, auth=(username, password))
        if response.status_code != 201:
            log.error(response.content)
            log.error('ERROR: %s: %s', response.status_code, response.reason)
            sys.exit(1)
        else:
            data = response.json()
            KytosConfig().save_token(username, data.get('hash'))
            return data.get('hash')
