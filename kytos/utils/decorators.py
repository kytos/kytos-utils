"""Decorators for Kytos-utils."""
import logging
import os
import sys
from getpass import getpass

import requests

from kytos.utils.config import KytosConfig

LOG = logging.getLogger(__name__)


# This class is used as decorator, so this class name is lowercase and the
# invalid-name warning from pylint is disabled below.
class kytos_auth:  # pylint: disable=invalid-name
    """Class to be used as decorator to require authentication."""

    def __init__(self, func):
        """Init method.

        Save the function on the func attribute and bootstrap a new config.
        """
        self.func = func
        self.config = KytosConfig().config
        self.cls = None
        self.obj = None

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

        # Ignore private attribute warning. We don't wanna make it public only
        # because of a decorator.
        config = self.obj._config  # pylint: disable=protected-access
        config.set('auth', 'user', user)
        config.set('auth', 'token', token)
        self.func.__call__(self.obj, *args, **kwargs)

    def __get__(self, instance, owner):
        """Deal with owner class."""
        self.cls = owner
        self.obj = instance

        return self.__call__

    def authenticate(self):
        """Check the user authentication."""
        endpoint = os.path.join(self.config.get('napps', 'api'), 'auth', '')
        username = self.config.get('auth', 'user')
        password = getpass("Enter the password for {}: ".format(username))
        response = requests.get(endpoint, auth=(username, password))
        if response.status_code != 201:
            LOG.error(response.content)
            LOG.error('ERROR: %s: %s', response.status_code, response.reason)
            sys.exit(1)
        else:
            data = response.json()
            KytosConfig().save_token(username, data.get('hash'))
            return data.get('hash')
