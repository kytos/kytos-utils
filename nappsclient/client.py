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

from urllib.parse import urljoin

import json
import requests
import sys
import os

class KytosClient():
    def __init__(self, api_uri, debug=False):
        self.api_uri = api_uri
        self.debug = debug

        if self.debug:
            self.set_debug()

    def set_debug(self):
        self.debug = sys.stderr

    def set_token(self, token):
        self.token = token

    def request_token(self, username, password):
        endpoint = urljoin(self.api_uri, '/auth/')

        request = requests.post(endpoint, auth=(username, password))
        if request.status_code != 201:
            print("ERROR: %d: %s" % (request.status_code, request.reason))
            sys.exit()

        json = request.json()
        self.set_token(json)
        return json

    def upload_napp(self, *args):
        endpoint = urljoin(self.api_uri, '/napps/')
        metadata = self.create_metadata()

        request = requests.post(endpoint, json=metadata)
        if request.status_code != 201:
            print("ERROR: %d: %s" % (request.status_code, request.reason))
            sys.exit()
        print('SUCCESS: Napp was uploaded.')

    def delete_napp(self, *args):
        endpoint = urljoin(self.api_uri, '/napps/{}/{}/')

        metadata = self.create_metadata()
        endpoint = endpoint.format(metadata['author'],metadata['name'])

        request = requests.delete(endpoint, json=metadata)
        if request.status_code != 200:
            print('Error %d: %s' % (request.status_code, request.reason))
            sys.exit(1)

        print('SUCCESS: Napp was deleted.')

    def create_metadata(self, json_filename='kytos.json',
                        readme_filename = 'README.rst'):

        if not os.path.isfile(json_filename):
            print("ERROR: Could not access kytos.json file.")
            sys.exit(1)

        with open(json_filename) as json_file:
            metadata = json.load(json_file)
            metadata['token'] = self.token.get('hash')

        try:
            with open(readme_filename) as readme_file:
                metadata['readme'] = readme_file.read()
        except:
            metadata['readme'] = ''

        return metadata
