"""REST communication with NApps Server."""
# This file is part of kytos-utils.
#
# Copyright (c) 2016 by Kytos Team.
#
# Authors:
#    Beraldo Leal <beraldo AT ncc DOT unesp DOT br>
#
# kytos-utils is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kytos-utils is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#

import json
import logging
import os
import sys

import requests
from kytos.utils.config import KytosConfig
from kytos.utils.decorators import kytos_auth
from kytos.utils.exceptions import KytosException

log = logging.getLogger(__name__)


class NAppsClient():
    """Client for the NApps Server."""

    def __init__(self, config=None):
        """Set Kytos config."""
        if config is None:
            config = KytosConfig().config
        self._config = config

    def get_napps(self):
        """Get all NApps from the server."""
        endpoint = os.path.join(self._config.get('napps', 'api'), 'napps', '')
        res = self.make_request(endpoint)

        if res.status_code != 200:
            msg = 'Error getting NApps from server (%s) - %s'
            log.error(msg, res.status_code, res.reason)
            sys.exit(1)

        return json.loads(res.content)['napps']

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

        print("SUCCESS: NApp {}/{} uploaded.".format(metadata['author'],
                                                     metadata['name']))

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
        except response.exceptions.ConnectionError:
            log.error("Couldn't connect to NApps server %s.", endpoint)
            sys.exit(1)

        return response
