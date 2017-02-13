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

from kytos.utils.exceptions import KytosException
from kytos.utils.config import KytosConfig


log = logging.getLogger(__name__)


class NAppsClient():
    """Client for the NApps Server."""

    def __init__(self):
        """Get Kytos config."""
        self._config = KytosConfig().config

    def get_napps(self):
        """Get all NApps from the server."""
        endpoint = urljoin(self._config.get('napps', 'uri'), 'napps')
        res = self.make_request(endpoint)

        if res.status_code != 200:
            msg = 'Error getting NApps from server (%s) - %s'
            log.error(msg, res.status_code, res.reason)
            sys.exit(1)

        return json.loads(res.content)['napps']

    def get_napp(self, username, name):
        """Return napp metadata or None if not found."""
        api = self._config.get('napps', 'uri')
        napp_uri = '{}{}/{}/{}/'.format(api, 'napps', username, name)
        res = self.make_request(napp_uri)
        if res.status_code == 404:  # We need to know if NApp is not found
            return None
        elif res.status_code != 200:
            raise KytosException('Error getting %s/%s from server: (%d) - %s',
                                 username, name, res.status_code, res.reason)
        return json.loads(res.content)

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


class Downloader:
    """Download napps to be installed."""

    def __init__(self):
        """Keep record of temporary files."""
        self._tmp_paths = []
        api = KytosConfig().config.get('napps', 'uri')
        self._repo = urljoin(api, '/repo')

    def extract_server_napp(self, username, name):
        """Download, extract NApp and return the folder with kytos.json.

        Raise:
            urllib.error.HTTPError: If download does not succeed
        """
        log.info('Downloading %s...', url)

        filename = self._download(url)
        if zipfile.is_zipfile(filename):
            folder = self.unzip(filename)
        else:
            folder = filename
        return self._find_napp(folder, author, napp_name)

    def _download(self, url):
        filename, _ = urlretrieve(url)
        log.info('Download successful')
        self._tmp_paths.append(filename)
        return filename

    def _extract(self, filename):
        """Unzip ``filename`` and return its root folder."""
        log.info('Unzipping downloaded file')
        folder = mkdtemp(prefix='kytos')
        zipfile.ZipFile.extractall(folder, path=folder)
        self._tmp_paths.append(folder)
        return folder

    @staticmethod
    def _find_napp(folder, author, napp_name):
        folder = Path(napp_name)
        meta = None
        for meta in folder.glob('**/kytos.json'):
            with meta.open() as f:
                napp = json.load(f)
                if napp['author'] == author and napp['name'] == napp_name:
                    break
        if meta is None:
            raise FileNotFoundError('NApp not found after download')
        return meta.parent

    def cleanup(self):
        """Remove temporary files."""
        for entry in self._tmp_paths:
            if path.exists(entry):
                if isdir(entry):
                    shutil.rmtree(entry)
                else:
                    os.unlink(entry)

# https://napps.kytos.io/repo/kytos/of_ipv6drop-latest.napp
