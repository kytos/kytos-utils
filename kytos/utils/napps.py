"""Manage Network Application files."""
import json
import logging
import os
import pathlib
import re
import sys
import tarfile
import urllib
from http import HTTPStatus

# Disable pylint import checks that conflict with isort
# pylint: disable=ungrouped-imports,wrong-import-order
from jinja2 import Environment, FileSystemLoader
from ruamel.yaml import YAML

from kytos.utils.client import NAppsClient
from kytos.utils.config import KytosConfig
from kytos.utils.exceptions import KytosException
from kytos.utils.openapi import OpenAPI
from kytos.utils.settings import SKEL_PATH

LOG = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes,too-many-public-methods
class NAppsManager:
    """Deal with NApps at filesystem level and ask Kytos to (un)load NApps."""

    _NAPP_ENABLE = "api/kytos/core/napps/{}/{}/enable"
    _NAPP_DISABLE = "api/kytos/core/napps/{}/{}/disable"
    _NAPP_INSTALL = "api/kytos/core/napps/{}/{}/install"
    _NAPP_UNINSTALL = "api/kytos/core/napps/{}/{}/uninstall"
    _NAPPS_INSTALLED = "api/kytos/core/napps_installed"
    _NAPPS_ENABLED = "api/kytos/core/napps_enabled"
    _NAPP_METADATA = "api/kytos/core/napps/{}/{}/metadata/{}"

    def __init__(self):
        """Instance a new NAppsManager.

        This method do not need parameters.
        """
        self._config = KytosConfig().config
        self._kytos_api = self._config.get('kytos', 'api')

        self.user = None
        self.napp = None
        self.version = None

        # Automatically get from kytosd API when needed
        self.__local_enabled = None
        self.__local_installed = None

    @property
    def _enabled(self):
        if self.__local_enabled is None:
            self.__require_kytos_config()
        return self.__local_enabled

    @property
    def _installed(self):
        if self.__local_installed is None:
            self.__require_kytos_config()
        return self.__local_installed

    def __require_kytos_config(self):
        """Set path locations from kytosd API.

        It should not be called directly, but from properties that require a
        running kytosd instance.
        """
        if self.__local_enabled is None:
            uri = self._kytos_api + 'api/kytos/core/config/'
            try:
                ops = json.loads(urllib.request.urlopen(uri).read())
            except urllib.error.URLError as err:
                msg = f'Error connecting to Kytos daemon: {uri} {err.reason}'
                print(msg)
                sys.exit(1)
            self.__local_enabled = pathlib.Path(ops.get('napps'))
            self.__local_installed = pathlib.Path(ops.get('installed_napps'))

    def set_napp(self, user, napp, version=None):
        """Set info about NApp.

        Args:
            user (str): NApps Server username.
            napp (str): NApp name.
            version (str): NApp version.
        """
        self.user = user
        self.napp = napp
        self.version = version or 'latest'

    @property
    def napp_id(self):
        """Return a Identifier of NApp."""
        return '/'.join((self.user, self.napp))

    @staticmethod
    def _get_napps(napps_dir):
        """List of (username, napp_name) found in ``napps_dir``.

        Ex: [('kytos', 'of_core'), ('kytos', 'of_lldp')]
        """
        jsons = napps_dir.glob('*/*/kytos.json')
        return sorted(j.parts[-3:-1] for j in jsons)

    def get_enabled_local(self):
        """Sorted list of (username, napp_name) of enabled napps."""
        return self._get_napps(self._enabled)

    def get_installed_local(self):
        """Sorted list of (username, napp_name) of installed napps."""
        return self._get_napps(self._installed)

    def get_enabled(self):
        """Sorted list of (username, napp_name) of enabled napps."""
        uri = self._kytos_api + self._NAPPS_ENABLED

        try:
            response = urllib.request.urlopen(uri)
            if response.getcode() != 200:
                msg = "Error calling Kytos to check enabled NApps."
                raise KytosException(msg)

            content = json.loads(response.read())
            return sorted((c[0], c[1]) for c in content['napps'])
        except urllib.error.URLError as exception:
            LOG.error("Error checking installed NApps. Is Kytos running?")
            raise KytosException(exception)

    def get_installed(self):
        """Sorted list of (username, napp_name) of installed napps."""
        uri = self._kytos_api + self._NAPPS_INSTALLED

        try:
            response = urllib.request.urlopen(uri)
            if response.getcode() != 200:
                msg = "Error calling Kytos to check installed NApps."
                raise KytosException(msg)

            content = json.loads(response.read())
            return sorted((c[0], c[1]) for c in content['napps'])
        except urllib.error.URLError as exception:
            LOG.error("Error checking installed NApps. Is Kytos running?")
            raise KytosException(exception)

    def is_installed(self):
        """Whether a NApp is installed."""
        return (self.user, self.napp) in self.get_installed()

    def get_disabled(self):
        """Sorted list of (username, napp_name) of disabled napps.

        The difference of installed and enabled.
        """
        installed = set(self.get_installed())
        enabled = set(self.get_enabled())
        return sorted(installed - enabled)

    def dependencies(self, user=None, napp=None):
        """Get napp_dependencies from install NApp.

        Args:
            user(string)  A Username.
            napp(string): A NApp name.
        Returns:
            napps(list): List with tuples with Username and NApp name.
                         e.g. [('kytos'/'of_core'), ('kytos/of_l2ls')]

        """
        napps = self._get_napp_key('napp_dependencies', user, napp)
        return [tuple(napp.split('/')) for napp in napps]

    def get_description(self, user=None, napp=None):
        """Return the description from kytos.json."""
        return self._get_napp_key('description', user, napp)

    def get_version(self, user=None, napp=None):
        """Return the version from kytos.json."""
        return self._get_napp_key('version', user, napp) or 'latest'

    def _get_napp_key(self, key, user=None, napp=None):
        """Return a value from kytos.json.

        Args:
            user (string): A Username.
            napp (string): A NApp name
            key (string): Key used to get the value within kytos.json.

        Returns:
            meta (object): Value stored in kytos.json.

        """
        if user is None:
            user = self.user
        if napp is None:
            napp = self.napp

        uri = self._kytos_api + self._NAPP_METADATA
        uri = uri.format(user, napp, key)

        meta = json.loads(urllib.request.urlopen(uri).read())
        return meta[key]

    def disable(self):
        """Disable a NApp if it is enabled."""
        uri = self._kytos_api + self._NAPP_DISABLE
        uri = uri.format(self.user, self.napp)

        try:
            json.loads(urllib.request.urlopen(uri).read())
        except urllib.error.HTTPError as exception:
            if exception.code == HTTPStatus.BAD_REQUEST.value:
                LOG.error("NApp is not installed. Check the NApp list.")
            else:
                LOG.error("Error disabling the NApp")

    def enable(self):
        """Enable a NApp if not already enabled."""
        uri = self._kytos_api + self._NAPP_ENABLE
        uri = uri.format(self.user, self.napp)

        try:
            json.loads(urllib.request.urlopen(uri).read())
        except urllib.error.HTTPError as exception:
            if exception.code == HTTPStatus.BAD_REQUEST.value:
                LOG.error("NApp is not installed. Check the NApp list.")
            else:
                LOG.error("Error enabling the NApp")

    def enabled_dir(self):
        """Return the enabled dir from current napp."""
        return self._enabled / self.user / self.napp

    def installed_dir(self):
        """Return the installed dir from current napp."""
        return self._installed / self.user / self.napp

    def is_enabled(self):
        """Whether a NApp is enabled."""
        return (self.user, self.napp) in self.get_enabled()

    def remote_uninstall(self):
        """Delete code inside NApp directory, if existent."""
        uri = self._kytos_api + self._NAPP_UNINSTALL
        uri = uri.format(self.user, self.napp)

        try:
            json.loads(urllib.request.urlopen(uri).read())
        except urllib.error.HTTPError as exception:
            if exception.code == HTTPStatus.BAD_REQUEST.value:
                LOG.error("Check if the NApp is installed.")
            else:
                LOG.error("Error uninstalling the NApp")

    @staticmethod
    def valid_name(username):
        """Check the validity of the given 'name'.

        The following checks are done:
        - name starts with a letter
        - name contains only letters, numbers or underscores
        """
        return username and re.match(r'[a-zA-Z][a-zA-Z0-9_]{2,}$', username)

    @staticmethod
    def render_template(templates_path, template_filename, context):
        """Render Jinja2 template for a NApp structure."""
        template_env = Environment(
            autoescape=False, trim_blocks=False,
            loader=FileSystemLoader(str(templates_path)))
        return template_env.get_template(str(template_filename)) \
            .render(context)

    @staticmethod
    def search(pattern):
        """Search all server NApps matching pattern.

        Args:
            pattern (str): Python regular expression.
        """
        def match(napp):
            """Whether a NApp metadata matches the pattern."""
            # WARNING: This will change for future versions, when 'author' will
            # be removed.
            username = napp.get('username', napp.get('author'))

            strings = ['{}/{}'.format(username, napp.get('name')),
                       napp.get('description')] + napp.get('tags')
            return any(pattern.match(string) for string in strings)

        napps = NAppsClient().get_napps()
        return [napp for napp in napps if match(napp)]

    def install_local(self):
        """Make a symlink in install folder to a local NApp.

        Raises:
            FileNotFoundError: If NApp is not found.

        """
        folder = self._get_local_folder()
        installed = self.installed_dir()
        self._check_module(installed.parent)
        installed.symlink_to(folder.resolve())

    def _get_local_folder(self, root=None):
        """Return local NApp root folder.

        Search for kytos.json in _./_ folder and _./user/napp_.

        Args:
            root (pathlib.pathlib.Path): Where to begin searching.

        Return:
            pathlib.pathlib.Path: NApp root folder.

        Raises:
            FileNotFoundError: If there is no such local NApp.

        """
        if root is None:
            root = pathlib.Path()
        for folders in ['.'], [self.user, self.napp]:
            kytos_json = root / pathlib.Path(*folders) / 'kytos.json'
            if kytos_json.exists():
                with kytos_json.open() as file_descriptor:
                    meta = json.load(file_descriptor)
                    # WARNING: This will change in future versions, when
                    # 'author' will be removed.
                    username = meta.get('username', meta.get('author'))
                    if username == self.user and meta.get('name') == self.napp:
                        return kytos_json.parent
        raise FileNotFoundError('kytos.json not found.')

    def remote_install(self):
        """Ask kytos server to install NApp."""
        uri = self._kytos_api + self._NAPP_INSTALL
        uri = uri.format(self.user, self.napp)

        try:
            json.loads(urllib.request.urlopen(uri).read())
        except urllib.error.HTTPError as exception:
            if exception.code == HTTPStatus.BAD_REQUEST.value:
                LOG.error("NApp is not installed. Check the NApp list.")
            else:
                LOG.error("Error installing the NApp.")

    @classmethod
    def create_napp(cls, meta_package=False):
        """Bootstrap a basic NApp structure for you to develop your NApp.

        This will create, on the current folder, a clean structure of a NAPP,
        filling some contents on this structure.
        """
        templates_path = SKEL_PATH / 'napp-structure/username/napp'

        ui_templates_path = os.path.join(templates_path, 'ui')

        username = None
        napp_name = None

        print('--------------------------------------------------------------')
        print('Welcome to the bootstrap process of your NApp.')
        print('--------------------------------------------------------------')
        print('In order to answer both the username and the napp name,')
        print('You must follow this naming rules:')
        print(' - name starts with a letter')
        print(' - name contains only letters, numbers or underscores')
        print(' - at least three characters')
        print('--------------------------------------------------------------')
        print('')
        while not cls.valid_name(username):
            username = input('Please, insert your NApps Server username: ')

        while not cls.valid_name(napp_name):
            napp_name = input('Please, insert your NApp name: ')

        description = input('Please, insert a brief description for your'
                            'NApp [optional]: ')
        if not description:
            # pylint: disable=fixme
            description = '# TODO: <<<< Insert your NApp description here >>>>'
            # pylint: enable=fixme

        context = {'username': username, 'napp': napp_name,
                   'description': description}

        #: Creating the directory structure (username/napp_name)
        os.makedirs(username, exist_ok=True)

        #: Creating ``__init__.py`` files
        with open(os.path.join(username, '__init__.py'), 'w') as init_file:
            init_file.write(f'"""Napps for the user {username}.""""')

        os.makedirs(os.path.join(username, napp_name))

        #: Creating the other files based on the templates
        templates = os.listdir(templates_path)
        templates.remove('ui')
        templates.remove('openapi.yml.template')

        if meta_package:
            templates.remove('main.py.template')
            templates.remove('settings.py.template')

        for tmp in templates:
            fname = os.path.join(username, napp_name,
                                 tmp.rsplit('.template')[0])
            with open(fname, 'w') as file:
                content = cls.render_template(templates_path, tmp, context)
                file.write(content)

        if not meta_package:
            NAppsManager.create_ui_structure(username, napp_name,
                                             ui_templates_path, context)

        print()
        print(f'Congratulations! Your NApp has been bootstrapped!\nNow you '
              'can go to the directory {username}/{napp_name} and begin to '
              'code your NApp.')
        print('Have fun!')

    @classmethod
    def create_ui_structure(cls, username, napp_name, ui_templates_path,
                            context):
        """Create the ui directory structure."""
        for section in ['k-info-panel', 'k-toolbar', 'k-action-menu']:
            os.makedirs(os.path.join(username, napp_name, 'ui', section))

        templates = os.listdir(ui_templates_path)

        for tmp in templates:
            fname = os.path.join(username, napp_name, 'ui',
                                 tmp.rsplit('.template')[0])

            with open(fname, 'w') as file:
                content = cls.render_template(ui_templates_path, tmp,
                                              context)
                file.write(content)

    @staticmethod
    def _check_module(folder):
        """Create module folder with empty __init__.py if it doesn't exist.

        Args:
            folder (pathlib.pathlib.Path): Module path.
        """
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True, mode=0o755)
            (folder / '__init__.py').touch()

    @staticmethod
    def build_napp_package(napp_name):
        """Build the .napp file to be sent to the napps server.

        Args:
            napp_identifier (str): Identifier formatted as
                <username>/<napp_name>

        Return:
            file_payload (binary): The binary representation of the napp
                package that will be POSTed to the napp server.

        """
        files = []
        path = os.getcwd()

        for dir_file in os.walk(path):
            dirname, _, arc = dir_file
            files.extend([os.path.join(dirname, f) for f in arc])

        # Allow the user to run `kytos napps upload` from outside the
        # napp directory.
        # Filter the files with the napp_name in their path
        # Example: home/user/napps/kytos/, napp_name = kronos
        # This filter will get all files from:
        # home/user/napps/kytos/kronos/*
        files = list(filter(lambda x: napp_name in x, files))

        ignored_files = [".git"]
        with open(".gitignore", 'r') as kytosignore:
            for line in kytosignore:
                # continue if the line starts with # or contains only spaces
                # or nothing
                if re.search(r"^(#+|\s*$)", line):
                    continue
                # replace to '' if the character is * or / in the begin or
                # / or \n in the end of line.
                line = re.sub(r"^([*]|/)|(/|\n)$", '', line)
                ignored_files.append(line)
        for filename in files.copy():
            for line in ignored_files:
                if re.search(line+"$", filename):
                    files.remove(filename)
                    break
        # Create the '.napp' package
        napp_file = tarfile.open(napp_name + '.napp', 'x:xz')
        for local_f in files:
            # Add relative paths instead of absolute paths
            napp_file.add(pathlib.PurePosixPath(local_f).relative_to(path))
        napp_file.close()

        # Get the binary payload of the package
        file_payload = open(napp_name + '.napp', 'rb')

        # remove the created package from the filesystem
        os.remove(napp_name + '.napp')

        return file_payload

    @staticmethod
    def create_metadata(*args, **kwargs):  # pylint: disable=unused-argument
        """Generate the metadata to send the napp package."""
        json_filename = kwargs.get('json_filename', 'kytos.json')
        readme_filename = kwargs.get('readme_filename', 'README.rst')
        ignore_json = kwargs.get('ignore_json', False)
        metadata = {}

        if not ignore_json:
            try:
                with open(json_filename) as json_file:
                    metadata = json.load(json_file)
            except FileNotFoundError:
                print("ERROR: Could not access kytos.json file.")
                sys.exit(1)

        try:
            with open(readme_filename) as readme_file:
                metadata['readme'] = readme_file.read()
        except FileNotFoundError:
            metadata['readme'] = ''

        try:
            yaml = YAML(typ='safe')
            openapi_dict = yaml.load(pathlib.Path('openapi.yml').open())
            openapi = json.dumps(openapi_dict)
        except FileNotFoundError:
            openapi = ''
        metadata['OpenAPI_Spec'] = openapi

        return metadata

    def upload(self, *args, **kwargs):
        """Create package and upload it to NApps Server.

        Raises:
            FileNotFoundError: If kytos.json is not found.

        """
        self.prepare()
        metadata = self.create_metadata(*args, **kwargs)
        package = self.build_napp_package(metadata.get('name'))

        NAppsClient().upload_napp(metadata, package)

    def delete(self):
        """Delete a NApp.

        Raises:
            requests.HTTPError: When there's a server error.

        """
        client = NAppsClient(self._config)
        client.delete(self.user, self.napp)

    @classmethod
    def prepare(cls):
        """Prepare NApp to be uploaded by creating openAPI skeleton."""
        if cls._ask_openapi():
            napp_path = pathlib.Path()
            tpl_path = SKEL_PATH / 'napp-structure/username/napp'
            OpenAPI(napp_path, tpl_path).render_template()
            print('Please, update your openapi.yml file.')
            sys.exit()

    @staticmethod
    def _ask_openapi():
        """Return whether we should create a (new) skeleton."""
        if pathlib.Path('openapi.yml').exists():
            question = 'Override local openapi.yml with a new skeleton? (y/N) '
            default = False
        else:
            question = 'Do you have REST endpoints and wish to create an API' \
                ' skeleton in openapi.yml? (Y/n) '
            default = True

        while True:
            answer = input(question)
            if answer == '':
                return default
            if answer.lower() in ['y', 'yes']:
                return True
            if answer.lower() in ['n', 'no']:
                return False

    def reload(self, napps=None):
        """Reload a NApp or all NApps.

        Args:
            napps (list): NApp list to be reloaded.
        Raises:
            requests.HTTPError: When there's a server error.

        """
        client = NAppsClient(self._config)
        client.reload_napps(napps)


# pylint: enable=too-many-instance-attributes,too-many-public-methods
