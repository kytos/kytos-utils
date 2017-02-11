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
import sys
from urllib.parse import urljoin

import requests

from kytos.utils.config import KytosConfig

log = logging.getLogger(__name__)


class KytosClient():
    """Client for the NApps Server."""

    def __init__(self):
        """Get Kytos config."""
        self._config = KytosConfig().config

    def get_napps(self):
        """Get all NApps from the server."""
        endpoint = urljoin(self._config.get('napps', 'uri'), 'napps')
        request = self.make_request(endpoint)

        if request.status_code != 200:
            msg = 'Error getting NApps from server (code %s): %s'
            log.error(msg, request.status_code, request.reason)
            sys.exit(1)

        return json.loads(request.content)['napps']

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
