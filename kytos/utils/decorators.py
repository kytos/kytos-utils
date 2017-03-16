from getpass import getpass
import logging
import sys

from urllib.parse import urljoin

import requests
from kytos.utils.config import KytosConfig

log = logging.getLogger(__name__)


class kytos_auth:
    """Class to be used as decorator to require authentication."""

    def __init__(self, func):
        self.func = func
        self.config = KytosConfig().config

    def __call__(self, *args, **kwargs):
        if not self.config.has_option('napps', 'uri'):
            self.config.set('napps', 'uri',
                            input("Enter the kytos napps server address: "))

        if not self.config.has_option('auth', 'user'):
            user = input("Enter the username: ")
            self.config.set('auth', 'user', user)
        else:
            user = self.config.get('auth', 'user')

        if not self.config.has_option('auth', 'token'):
            token = self.authenticate()
        else:
            token = self.config.get('auth', 'token')

        self.obj._config.set('auth', 'user', user)
        self.obj._config.set('auth', 'token', token)
        self.func.__call__(self.obj, *args, **kwargs)

    def __get__(self, instance, owner):
        self.cls = owner
        self.obj = instance

        return self.__call__

    def authenticate(self):
        endpoint = urljoin(self.config.get('napps', 'uri'), '/api/auth/')
        username = self.config.get('auth', 'user')
        password = getpass("Enter the password for {}: ".format(username))
        request = requests.post(endpoint, auth=(username, password))
        if request.status_code != 201:
            log.error('ERROR: %s: %s', request.status_code, request.reason)
            sys.exit(1)
        else:
            data = request.json()
            KytosConfig().save_token(username, data.get('hash'))
            return data.get('hash')
