"""REST communication with NApps Server."""
# This file is part of kytos-utils.
#
# Copyright (c) 2016 by Kytos Team.
#
# Authors:
#    Beraldo Leal <beraldo AT ncc DOT unesp DOT br>

import json
import logging
import os
import sys

import requests

from kytos.utils.config import KytosConfig
from kytos.utils.decorators import kytos_auth
from kytos.utils.exceptions import KytosException

log = logging.getLogger(__name__)


class CommonClient:
    """Generic class used to make request the Napss server."""

    def __init__(self, config=None):
        """Set Kytos config."""
        if config is None:
            config = KytosConfig().config
        self._config = config

    @staticmethod
    def make_request(endpoint, **kwargs):
        """Send a request to server."""
        data = kwargs.get('json', [])
        package = kwargs.get('package', None)
        method = kwargs.get('method', 'GET')

        function = getattr(requests, method.lower())

        try:
            if package:
                response = function(endpoint, data=data,
                                    files={'file': package})
            else:
                response = function(endpoint, json=data)
        except requests.exceptions.ConnectionError:
            log.error("Couldn't connect to NApps server %s.", endpoint)
            sys.exit(1)

        return response


class NAppsClient(CommonClient):
    """Client for the NApps Server."""

    def get_napps(self):
        """Get all NApps from the server."""
        endpoint = os.path.join(self._config.get('napps', 'api'), 'napps', '')
        res = self.make_request(endpoint)

        if res.status_code != 200:
            msg = 'Error getting NApps from server (%s) - %s'
            log.error(msg, res.status_code, res.reason)
            sys.exit(1)

        return json.loads(res.content.decode('utf-8'))['napps']

    def get_napp(self, username, name):
        """Return napp metadata or None if not found."""
        endpoint = os.path.join(self._config.get('napps', 'api'), 'napps',
                                username, name, '')
        res = self.make_request(endpoint)
        if res.status_code == 404:  # We need to know if NApp is not found
            return None
        elif res.status_code != 200:
            raise KytosException('Error getting %s/%s from server: (%d) - %s',
                                 username, name, res.status_code, res.reason)
        return json.loads(res.content)

    @kytos_auth
    def upload_napp(self, metadata, package):
        """Upload the napp from the current directory to the napps server."""
        endpoint = os.path.join(self._config.get('napps', 'api'), 'napps', '')
        metadata['token'] = self._config.get('auth', 'token')
        request = self.make_request(endpoint, json=metadata, package=package,
                                    method="POST")
        if request.status_code != 201:
            KytosConfig().clear_token()
            log.error("%s: %s", request.status_code, request.reason)
            sys.exit(1)

        # WARNING: this will change in future versions, when 'author' will get
        # removed.
        username = metadata.get('username', metadata.get('author'))
        name = metadata.get('name')

        print("SUCCESS: NApp {}/{} uploaded.".format(username, name))

    @kytos_auth
    def delete(self, username, napp):
        """Delete a NApp.

        Raises:
            requests.HTTPError: If 400 <= status < 600.
        """
        api = self._config.get('napps', 'api')
        endpoint = os.path.join(api, 'napps', username, napp, '')
        content = {'token': self._config.get('auth', 'token')}
        response = self.make_request(endpoint, json=content, method='DELETE')
        response.raise_for_status()


class UsersClient(CommonClient):
    """Client for the NApps Server."""

    def register(self, user_dict):
        """Send an user_dict to NApps server using POST request.

        Args:
            user_dict(dict): Dictionary with user attributes.
        Returns:
            result(string): Return the response of Napps server.
        """
        endpoint = os.path.join(self._config.get('napps', 'api'), 'users', '')
        res = self.make_request(endpoint, method='POST', json=user_dict)

        return res.content.decode('utf-8')
