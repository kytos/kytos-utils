"""Setup script.

Run "python3 setup --help-commands" to list all available commands and their
descriptions.
"""
import os
from abc import abstractmethod
# Disabling checks due to https://github.com/PyCQA/pylint/issues/73
from distutils.command.clean import clean  # pylint: disable=E0401,E0611
from subprocess import call

from setuptools import Command, find_packages, setup
from setuptools.command.develop import develop

if 'VIRTUAL_ENV' in os.environ:
    BASE_ENV = os.environ['VIRTUAL_ENV']
else:
    BASE_ENV = '/'

SKEL_PATH = 'etc/skel'
KYTOS_SKEL_PATH = os.path.join(SKEL_PATH, 'kytos')
USERNAME_PATH = os.path.join(KYTOS_SKEL_PATH, 'napp-structure/username')
NAPP_PATH = os.path.join(USERNAME_PATH, 'napp')
ETC_FILES = [(os.path.join(BASE_ENV, USERNAME_PATH),
              [os.path.join(USERNAME_PATH, '__init__.py')]),
             (os.path.join(BASE_ENV, NAPP_PATH),
              [os.path.join(NAPP_PATH, '__init__.py'),
               os.path.join(NAPP_PATH, 'kytos.json.template'),
               os.path.join(NAPP_PATH, 'main.py.template'),
               os.path.join(NAPP_PATH, 'README.rst.template'),
               os.path.join(NAPP_PATH, 'settings.py.template')])]


class SimpleCommand(Command):
    """Make Command implementation simpler."""

    user_options = []

    @abstractmethod
    def run(self):
        """Run when command is invoked.

        Use *call* instead of *check_call* to ignore failures.
        """
        pass

    def initialize_options(self):
        """Set defa ult values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass


class Cleaner(clean):
    """Custom clean command to tidy up the project root."""

    description = 'clean build, dist, pyc and egg from package and docs'

    def run(self):
        """Clean build, dist, pyc and egg from package and docs."""
        super().run()
        call('rm -vrf ./build ./dist ./*.egg-info', shell=True)
        call('find . -name __pycache__ -type d | xargs rm -rf', shell=True)
        call('test -d docs && make -C docs/ clean', shell=True)


class TestCoverage(SimpleCommand):
    """Display test coverage."""

    description = 'run unit tests and display code coverage'

    def run(self):
        """Run unittest quietly and display coverage report."""
        cmd = 'coverage3 run -m unittest discover -qs tests' \
              ' && coverage3 report'
        call(cmd, shell=True)


class Linter(SimpleCommand):
    """Code linters."""

    description = 'lint Python source code'

    def run(self):
        """Run pylama."""
        print('Pylama is running. It may take several seconds...')
        call('pylama setup.py tests kytos', shell=True)


class DevelopMode(develop):
    """Recommended setup for kytos-utils developers.

    Instead of copying the files to the expected directories, a symlink is
    created on the system aiming the current source code.
    """

    def run(self):
        """Install the package in a developer mode."""
        super().run()
        self._create_data_files_directory()

    @staticmethod
    def _create_data_files_directory():
        current_directory = os.path.abspath(os.path.dirname(__file__))

        etc_dir = os.path.join(BASE_ENV, 'etc')
        if not os.path.exists(etc_dir):
            os.mkdir(etc_dir)

        dst_dir = os.path.join(BASE_ENV, SKEL_PATH)
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)

        src = os.path.join(current_directory, KYTOS_SKEL_PATH)
        dst = os.path.join(BASE_ENV, KYTOS_SKEL_PATH)

        if not os.path.exists(dst):
            os.symlink(src, dst)


REQS = [i.strip() for i in open("requirements.txt").readlines()]

setup(name='kytos-utils',
      version='2017.1b3',
      description='Command line utilities to use with Kytos.',
      url='http://github.com/kytos/kytos-utils',
      author='Kytos Team',
      author_email='devel@lists.kytos.io',
      license='MIT',
      test_suite='tests',
      include_package_data=True,
      scripts=['bin/kytos'],
      install_requires=REQS,
      data_files=ETC_FILES,
      packages=find_packages(exclude=['tests']),
      cmdclass={
          'clean': Cleaner,
          'coverage': TestCoverage,
          'develop': DevelopMode,
          'lint': Linter
      },
      zip_safe=False)
