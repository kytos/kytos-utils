from getpass import getpass
import logging
import sys

from urllib.parse import urljoin

import requests

log = logging.getLogger(__name__)


class kytos_auth:
    """Class to be used as decorator to require authentication."""

    def __init__(self, func):
        self.func = func
        self.config = func._config.config

    def __call__(self):
        if not self.config.has_option('napps', 'uri'):
            self.config.set('napps', 'uri',
                            input("Enter the kytos napps server address: "))

        if not self.config.has_option('auth', 'user'):
            self.config.set('auth', 'user', input("Enter the username: "))

        if not self.config.has_option('auth', 'token'):
            self.authenticate()

    def authenticate(self):
        endpoint = urljoin(self.config.get('napps', 'uri'), '/api/auth/')
        username = self.config.get('auth', 'username')
        password = getpass("Enter the password for %s: " % self.config.user)
        request = requests.post(endpoint, auth=(username, password))
        if request.status_code != 201:
            log.error('%s: %s', request.status_code, request.reason)
            sys.exit()
        else:
            json = request.json()
            self.config.save_token(username, json.get('hash'))
