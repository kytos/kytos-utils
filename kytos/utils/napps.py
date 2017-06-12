"""Manage Network Application files."""
import json
import logging
import os
import re
import shutil
import sys
import tarfile
import urllib
from pathlib import Path
from random import randint

from jinja2 import Environment, FileSystemLoader

from kytos.utils.client import NAppsClient
from kytos.utils.config import KytosConfig

log = logging.getLogger(__name__)


class NAppsManager:
    """Deal with NApps at filesystem level and ask Kytos to (un)load NApps."""

    def __init__(self, controller=None):
        """If controller is not informed, the necessary paths must be.

        If ``controller`` is available, NApps will be (un)loaded at runtime and
        you don't need to inform the paths. Otherwise, you should inform the
        required paths for the methods called.

        Args:
            controller (kytos.Controller): Controller to (un)load NApps.
            install_path (str): Folder where NApps should be installed. If
                None, use the controller's configuration.
            enabled_path (str): Folder where enabled NApps are stored. If None,
                use the controller's configuration.
        """
        self._controller = controller
        self._config = KytosConfig().config
        self._kytos_api = self._config.get('kytos', 'api')
        self._load_kytos_configuration()

        self.user = None
        self.napp = None

    def _load_kytos_configuration(self):
        """Request current configurations loaded by Kytos instance."""
        uri = self._kytos_api + 'kytos/config/'
        try:
            options = json.loads(urllib.request.urlopen(uri).read())
        except urllib.error.URLError:
            print('Kytos is not running.')
            sys.exit()

        self._installed = Path(options.get('installed_napps'))
        self._enabled = Path(options.get('napps'))

    def set_napp(self, user, napp):
        """Set info about NApp.

        Args:
            user (str): NApps Server username.
            napp (str): NApp name.
        """
        self.user = user
        self.napp = napp

    @property
    def napp_id(self):
        """Identifier of NApp."""
        return '/'.join((self.user, self.napp))

    @staticmethod
    def _get_napps(napps_dir):
        """List of (username, napp_name) found in ``napps_dir``."""
        jsons = napps_dir.glob('*/*/kytos.json')
        return sorted(j.parts[-3:-1] for j in jsons)

    def get_enabled(self):
        """Sorted list of (username, napp_name) of enabled napps."""
        return self._get_napps(self._enabled)

    def get_installed(self):
        """Sorted list of (username, napp_name) of installed napps."""
        return self._get_napps(self._installed)

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
        """Method used to get napp_dependencies from install NApp.

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

    def _get_napp_key(self, key, user=None, napp=None):
        """Generic method used to return a value from kytos.json.

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
        kj = self._installed / user / napp / 'kytos.json'
        try:
            with kj.open() as f:
                meta = json.load(f)
                return meta[key]
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return ''

    def disable(self):
        """Disable a NApp if it is enabled."""
        enabled = self.enabled_dir()
        try:
            enabled.unlink()
            if self._controller is not None:
                self._controller.unload_napp(self.user, self.napp)
        except FileNotFoundError:
            pass  # OK, it was already disabled

    def enabled_dir(self):
        """Return the enabled dir from current napp."""
        return self._enabled / self.user / self.napp

    def installed_dir(self):
        """Return the installed dir from current napp."""
        return self._installed / self.user / self.napp

    def enable(self):
        """Enable a NApp if not already enabled.

        Raises:
            FileNotFoundError: If NApp is not installed.
            PermissionError: No filesystem permission to enable NApp.
        """
        enabled = self.enabled_dir()
        installed = self.installed_dir()

        if not installed.is_dir():
            raise FileNotFoundError('Install NApp {} first.'.format(
                self.napp_id))
        elif not enabled.exists():
            self._check_module(enabled.parent)
            try:
                # Create symlink
                enabled.symlink_to(installed)
                if self._controller is not None:
                    self._controller.load_napp(self.user, self.napp)
            except FileExistsError:
                pass  # OK, NApp was already enabled
            except PermissionError:
                raise PermissionError('Permission error on enabling NApp. Try '
                                      'with sudo.')

    def is_enabled(self):
        """Whether a NApp is enabled."""
        return (self.user, self.napp) in self.get_enabled()

    def uninstall(self):
        """Delete code inside NApp directory, if existent."""
        if self.is_installed():
            installed = self.installed_dir()
            if installed.is_symlink():
                installed.unlink()
            else:
                shutil.rmtree(str(installed))

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
        TEMPLATE_ENV = Environment(autoescape=False, trim_blocks=False,
                                   loader=FileSystemLoader(templates_path))
        return TEMPLATE_ENV.get_template(template_filename).render(context)

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
            root (pathlib.Path): Where to begin searching.

        Raises:
            FileNotFoundError: If there is no such local NApp.

        Return:
            pathlib.Path: NApp root folder.
        """
        if root is None:
            root = Path()
        for folders in ['.'], [self.user, self.napp]:
            kytos_json = root / Path(*folders) / 'kytos.json'
            if kytos_json.exists():
                with kytos_json.open() as f:
                    meta = json.load(f)
                    # WARNING: This will change in future versions, when
                    # 'author' will be removed.
                    username = meta.get('username', meta.get('author'))
                    if username == self.user and meta.get('name') == self.napp:
                        return kytos_json.parent
        raise FileNotFoundError('kytos.json not found.')

    def install_remote(self):
        """Download, extract and install NApp."""
        package, pkg_folder = None, None
        try:
            package = self._download()
            pkg_folder = self._extract(package)
            napp_folder = self._get_local_folder(pkg_folder)
            dst = self._installed / self.user / self.napp
            self._check_module(dst.parent)
            shutil.move(str(napp_folder), str(dst))
        finally:
            # Delete temporary files
            if package:
                Path(package).unlink()
            if pkg_folder and pkg_folder.exists():
                shutil.rmtree(str(pkg_folder))

    def _download(self):
        """Download NApp package from server.

        Raises:
            urllib.error.HTTPError: If download is not successful.

        Return:
            str: Downloaded temp filename.
        """
        repo = self._config.get('napps', 'repo')
        uri = os.path.join(repo, self.user, '{}-latest.napp'.format(self.napp))
        return urllib.request.urlretrieve(uri)[0]

    @staticmethod
    def _extract(filename):
        """Extract package to a temporary folder.

        Return:
            pathlib.Path: Temp dir with package contents.
        """
        random_string = '{:0d}'.format(randint(0, 10**6))
        tmp = '/tmp/kytos-napp-' + Path(filename).stem + '-' + random_string
        os.mkdir(tmp)
        with tarfile.open(filename, 'r:xz') as tar:
            tar.extractall(tmp)
        return Path(tmp)

    @classmethod
    def create_napp(cls):
        """Bootstrap a basic NApp strucutre for you to develop your NApp.

        This will create, on the current folder, a clean structure of a NAPP,
        filling some contents on this structure.
        """
        base = os.environ.get('VIRTUAL_ENV', '/')

        templates_path = os.path.join(base, 'etc', 'skel', 'kytos',
                                      'napp-structure', 'username', 'napp')
        username = None
        napp_name = None
        description = None
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
        msg = 'Please, insert your NApps Server username: '
        while not cls.valid_name(username):
            username = input(msg)

        while not cls.valid_name(napp_name):
            napp_name = input('Please, insert your NApp name: ')

        msg = 'Please, insert a brief description for your NApp [optional]: '
        description = input(msg)
        if not description:
            description = \
                '# TODO: <<<< Insert here your NApp description >>>>'  # noqa

        context = {'username': username, 'napp': napp_name,
                   'description': description}

        #: Creating the directory structure (username/napp_name)
        os.makedirs(username, exist_ok=True)
        #: Creating ``__init__.py`` files
        with open(os.path.join(username, '__init__.py'), 'w'):
            pass

        os.makedirs(os.path.join(username, napp_name))
        with open(os.path.join(username, napp_name, '__init__.py'), 'w'):
            pass

        #: Creating the other files based on the templates
        templates = os.listdir(templates_path)
        templates.remove('__init__.py')
        for tmp in templates:
            fname = os.path.join(username, napp_name,
                                 tmp.rsplit('.template')[0])
            with open(fname, 'w') as file:
                content = cls.render_template(templates_path, tmp, context)
                file.write(content)

        msg = '\nCongratulations! Your NApp have been bootstrapped!\nNow you '
        msg += 'can go to the directory {}/{} and begin to code your NApp.'
        print(msg.format(username, napp_name))
        print('Have fun!')

    @staticmethod
    def _check_module(folder):
        """Create module folder with empty __init__.py if it doesn't exist.

        Args:
            folder (pathlib.Path): Module path.
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
        for local_f in files:
            napp_file.add(local_f)
        napp_file.close()

        # Get the binary payload of the package
        file_payload = open(napp_name + '.napp', 'rb')

        # remove the created package from the filesystem
        os.remove(napp_name + '.napp')

        return file_payload

    @staticmethod
    def create_metadata(*args, **kwargs):
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

        return metadata

    def upload(self, *args, **kwargs):
        """Create package and upload it to NApps Server.

        Raises:
            FileNotFoundError: If kytos.json is not found.
        """
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
