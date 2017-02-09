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
import os
import re
import requests
import sys
import tarfile

from jinja2 import Environment, FileSystemLoader
from urllib.parse import urljoin


if 'VIRTUAL_ENV' in os.environ:
    BASE_ENV = os.environ['VIRTUAL_ENV']
else:
    BASE_ENV = '/'

TEMPLATES_PATH = os.path.join(BASE_ENV,
                              'etc/skel/kytos/napp-structure/author/napp')


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
        endpoint = urljoin(self.api_uri, '/api/auth/')

        request = requests.post(endpoint, auth=(username, password))
        if request.status_code != 201:
            print("ERROR: %d: %s" % (request.status_code, request.reason))
            sys.exit()

        json = request.json()
        self.set_token(json)
        return json

    def list_napps(self, *args):
        endpoint = urljoin(self.api_uri, '/api/napps/')
        metadata = self.create_metadata(ignore_json=True)
        author = args[0].author

        if author:
            endpoint = urljoin(endpoint, author+"/")

        request = self.make_request(endpoint, json=metadata)

        if request.status_code != 200:
            print("ERROR: %d: %s" % (request.status_code, request.reason))
            sys.exit(1)

        if author:
            napps = json.loads(request.content)
        else:
            napps = json.loads(request.content)['napps']

        self.print_napps_list(napps)

    def print_napps_list(self, napps):
        msg = "{:<20}|{:<12}|{:<50}|{:<10}|{:<50}"
        print(msg.format('Napp Name', 'Author', 'URL', 'Version',
                         'Description'))

        for napp in napps:
            if napp is str:
                continue
            author = napp.get('author', '')
            name = napp.get('name', '')
            url = napp.get('url', '')
            version = napp.get('version', '')
            desc = napp.get('description', '')

            print(msg.format(name, author, url, version, desc))

    @staticmethod
    def valid_name(name):
        """Check the validity of the given 'name'.

        The following checks are done:
        - name is not None and
        - name is not empty
        - name cannot contain spaces
        - name name does not start with underscore or numbers
        - name does not contain the following characters: -*.!@#$%&()[]\/
        """
        return name is not None and not name == '' and not \
            re.search(r'\s', name) and not re.match(r'[_0-9]', name) and not \
            re.search(r'[-*.!@#$%&()\[\]/\\]', name)

    @staticmethod
    def render_template(template_filename, context):
        """Renders Jinja2 template for a NApp structure."""
        TEMPLATE_ENV = Environment(autoescape=False, trim_blocks=False,
                                   loader=FileSystemLoader(TEMPLATES_PATH))
        return TEMPLATE_ENV.get_template(template_filename).render(context)

    def create_napp(self, *args):
        """Bootstrap a basic NApp strucutre for you to develop your NApp.

        This will create, on the current folder, a clean structure of a NAPP,
        filling some contents on this structure.
        """
        author = None
        napp_name = None
        description = None
        print('--------------------------------------------------------------')
        print('Welcome to the bootstrap process of your NApp.')
        print('--------------------------------------------------------------')
        print('In order to answer both the author name and the napp name,')
        print('You must follow this naming rules:')
        print(' - it cannot be empty')
        print(' - it cannot contain spaces')
        print(' - it cannot start with underscore or numbers')
        print(' - it cannot contain the following characters: -*.!@#$%&()[]\/')
        print('--------------------------------------------------------------')
        print('')
        msg = 'Please, insert you author name (username on the Napps Server): '
        while not self.valid_name(author):
            author = input(msg)

        while not self.valid_name(napp_name):
            napp_name = input('Please, insert you NApp name: ')

        msg = 'Please, insert a brief description for your NApp [optional]: '
        description = input(msg)
        if not description:
            description = '# TODO: <<<< Insert here your NApp description >>>>'

        context = {'author': author, 'napp': napp_name,
                   'description': description}

        #: Creating the directory structure (author/name)
        os.makedirs(author, exist_ok=True)
        #: Creating ``__init__.py`` files
        with open(os.path.join(author, '__init__.py'), 'w'):
            pass

        os.makedirs(os.path.join(author, napp_name))
        with open(os.path.join(author, napp_name, '__init__.py'), 'w'):
            pass

        #: Creating the other files based on the templates
        templates = os.listdir(TEMPLATES_PATH)
        templates.remove('__init__.py')
        for tmp in templates:
            fname = os.path.join(author, napp_name, tmp.rstrip('.template'))
            with open(fname, 'w') as file:
                content = self.render_template(tmp, context)
                file.write(content)

        msg = '\nCongratulations! Your NApp have been bootsrapped!\nNow you '
        msg += 'can go to the directory {}/{} and begin to code your NApp.'
        print(msg.format(author, napp_name))
        print('Have fun!')

    def upload_napp(self, *args):
        endpoint = urljoin(self.api_uri, '/api/napps/')
        metadata = self.create_metadata()
        package = self.build_package(metadata['name'])
        request = self.make_request(endpoint, json=metadata, package=package,
                                    method="POST")

        if request.status_code != 201:
            print("ERROR: %d: %s" % (request.status_code, request.reason))
            sys.exit(1)
        print('SUCCESS: Napp was uploaded.')

    def delete_napp(self, *args):
        endpoint = urljoin(self.api_uri, '/api/napps/{}/{}/')
        metadata = self.create_metadata()
        endpoint = endpoint.format(metadata['author'], metadata['name'])
        request = self.make_request(endpoint, json=metadata, method="DELETE")

        if request.status_code != 200:
            print('Error %d: %s' % (request.status_code, request.reason))
            sys.exit(1)
        print('SUCCESS: Napp was deleted.')

    def make_request(self, endpoint, **kwargs):
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
            print('Server Not found.')
            sys.exit(1)

        return response

    def create_metadata(self, **kwargs):
        json_filename = kwargs.get('json_filename', 'kytos.json')
        readme_filename = kwargs.get('readme_filename', 'README.rst')
        ignore_json = kwargs.get('ignore_json', False)
        metadata = {}

        if ignore_json is False:
            try:
                with open(json_filename) as json_file:
                    metadata = json.load(json_file)
            except FileNotFoundError:
                print("ERROR: Could not access kytos.json file.")
                sys.exit(1)

        metadata['token'] = self.token.get('hash')

        try:
            with open(readme_filename) as readme_file:
                metadata['readme'] = readme_file.read()
        except:
            metadata['readme'] = ''

        return metadata

    def build_package(self, napp_name):
        ignored_extensions = ['.swp', '.pyc', '.napp']
        ignored_dirs = ['__pycache__']
        files = os.listdir()
        for filename in files:
            if os.path.isfile(filename) and '.' in filename and \
                    filename.rsplit('.', 1)[1] in ignored_extensions:
                files.remove(filename)
            elif os.path.isdir(filename) and filename in ignored_dirs:
                files.remove(filename)

        # Create the '.napp' package
        napp_file = tarfile.open(napp_name + '.napp', 'x:xz')
        [napp_file.add(f) for f in files]
        napp_file.close()

        # Get the binary payload of the package
        file_payload = open(napp_name + '.napp', 'rb')

        # remove the created package from the filesystem
        os.remove(napp_name + '.napp')

        return file_payload
