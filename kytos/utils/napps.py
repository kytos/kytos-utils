"""Manage Network Application files."""
import logging
import os
import re
import shutil
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

log = logging.getLogger(__name__)


class NAppsManager:
    """Deal with NApps at filesystem level and ask Kyco to (un)load NApps."""

    def __init__(self, controller=None, install_path=None, enabled_path=None):
        """If controller is not informed, the necessary paths must be.

        If ``controller`` is available, NApps will be (un)loaded at runtime and
        you don't need to inform the paths. Otherwise, you should inform the
        required paths for the methods called.

        Args:
            controller (kyco.Controller): Controller to (un)load NApps.
            install_path (str): Folder where NApps should be installed. If
                None, use the controller's configuration.
            enabled_path (str): Folder where enabled NApps are stored. If None,
                use the controller's configuration.
        """
        self.controller = controller
        if controller is not None:
            if install_path is None:
                install_path = controller.options.installed_napps
            if enabled_path is None:
                enabled_path = controller.options.napps
        self._installed = Path(install_path) if install_path else None
        self._enabled = Path(enabled_path) if enabled_path else None

    @staticmethod
    def _get_napps(napps_dir):
        """List of (author, napp_name) found in ``napps_dir``."""
        jsons = napps_dir.glob('*/*/kytos.json')
        return sorted(j.parts[-3:-1] for j in jsons)

    def get_enabled(self):
        """Sorted list of (author, napp_name) of enabled napps."""
        return self._get_napps(self._enabled)

    def get_installed(self):
        """Sorted list of (author, napp_name) of installed napps."""
        return self._get_napps(self._installed)

    def is_installed(self, author, napp_name):
        """Whether a NApp is installed."""
        return (author, napp_name) in self.get_installed()

    def get_disabled(self):
        """Sorted list of (author, napp_name) of disabled napps.

        The difference of installed and enabled.
        """
        installed = set(self.get_installed())
        enabled = set(self.get_enabled())
        return sorted(installed - enabled)

    def disable(self, author, napp_name):
        """Disable a NApp by removing its symbolic link."""
        enabled = self._enabled / author / napp_name
        try:
            enabled.unlink()
            # TODO: Clean authors dir in a correct manner
            # self._clean_author(enabled.parent)
            log.info('Disabled NApp %s/%s', author, napp_name)

            if self.controller is not None:
                self.controller.unload_napp(author, napp_name)
        except FileNotFoundError:
            log.warning('NApp %s/%s was not enabled', author, napp_name)

    def enable(self, author, napp_name):
        """Enable a NApp by creating the a symbolic link."""
        enabled = self._enabled / author / napp_name
        installed = self._installed / author / napp_name

        if not installed.is_dir():
            log.error('Install NApp %s/%s first', author, napp_name)
        elif enabled.exists():
            log.warning('NApp %s/%s was already enabled', author, napp_name)
        else:
            # Make sure the enabled author/__init__.py exists.
            author = enabled.parent
            author.mkdir(exist_ok=True)
            init = author / '__init__.py'
            try:
                init.touch()
                # Create symlink
                enabled.symlink_to(installed)

                log.info('Enabled NApp %s/%s', author, napp_name)
                if self.controller is not None:
                    self.controller.load_napp(author, napp_name)
            except FileExistsError:
                pass  # No need to change the file modification time
            except PermissionError:
                log.error("You need permission to enable NApps")

    def uninstall(self, author, napp_name):
        """Disable and delete code inside NApp directory."""
        self.disable(author, napp_name)
        if self.is_installed(author, napp_name):
            installed = self._installed / author / napp_name
            shutil.rmtree(str(installed))
            # TODO: Clean authors dir in a correct manner
            # self._clean_author(installed.parent)
            log.info('Uninstalled NApp %s/%s')
        else:
            log.warning('NApp %s/%s was not installed', author, napp_name)

    def _clean_author(self, author_dir):
        """Remove author folder if there's no NApps inside."""
        if not self._get_napps(author_dir):
            shutil.rmtree(str(author_dir))

    @staticmethod
    def valid_name(name):
        """Check the validity of the given 'name'.

        The following checks are done:
        - name starts with a letter
        - name contains only letters, numbers or underscores
        """
        return name is not None and re.match(r'[a-zA-Z][a-zA-Z0-9_]{2,}$',
                                             name)

    @staticmethod
    def render_template(templates_path, template_filename, context):
        """Renders Jinja2 template for a NApp structure."""
        TEMPLATE_ENV = Environment(autoescape=False, trim_blocks=False,
                                   loader=FileSystemLoader(templates_path))
        return TEMPLATE_ENV.get_template(template_filename).render(context)

    @classmethod
    def create_napp(cls):
        """Bootstrap a basic NApp strucutre for you to develop your NApp.

        This will create, on the current folder, a clean structure of a NAPP,
        filling some contents on this structure.
        """

        base = os.environ.get('VIRTUAL_ENV') or '/'

        templates_path = os.path.join(base, 'etc', 'skel', 'kytos',
                                      'napp-structure', 'author', 'napp')
        author = None
        napp_name = None
        description = None
        print('--------------------------------------------------------------')
        print('Welcome to the bootstrap process of your NApp.')
        print('--------------------------------------------------------------')
        print('In order to answer both the author name and the napp name,')
        print('You must follow this naming rules:')
        print(' - name starts with a letter')
        print(' - name contains only letters, numbers or underscores')
        print(' - at least three characters')
        print('--------------------------------------------------------------')
        print('')
        msg = 'Please, insert you author name (username on the Napps Server): '
        while not cls.valid_name(author):
            author = input(msg)

        while not cls.valid_name(napp_name):
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
        templates = os.listdir(templates_path)
        templates.remove('__init__.py')
        for tmp in templates:
            fname = os.path.join(author, napp_name, tmp.rsplit('.template')[0])
            with open(fname, 'w') as file:
                content = cls.render_template(templates_path, tmp, context)
                file.write(content)

        msg = '\nCongratulations! Your NApp have been bootsrapped!\nNow you '
        msg += 'can go to the directory {}/{} and begin to code your NApp.'
        print(msg.format(author, napp_name))
        print('Have fun!')
