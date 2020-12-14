"""Translate cli commands to non-cli code."""
import re
import subprocess


class BugReportAPI:
    """Retrieve Kytos environment information.

    Collect system information, python environment, python packages and
    installed NApps to print this report to the user, aiming to improve
    bug reports.
    """

    @classmethod
    def bug_report(cls, _):
        """Run all reports."""
        cls.system_report()
        cls.python_environment()
        cls.python_packages_report()
        cls.kytos_environment_report()

    @classmethod
    def system_report(cls):
        """Display system information.

        Print distribution release system information.
        """
        print('# Platform')
        lsb_release = cls._execute('lsb_release -a 2> /dev/null')
        uname = cls._execute('uname -a')
        print('## Release information')
        print(lsb_release)
        print('## System Information')
        print(uname)

    @classmethod
    def python_environment(cls):
        """Display python environment report.

        This method shows the path and version of pip and python.
        """
        cls._print_path_and_version('python')
        cls._print_path_and_version('pip')

    @classmethod
    def _print_path_and_version(cls, package):
        """Display a package path and version."""
        print('## '+package.title())
        path = cls._execute(f'which {package}')
        version = cls._execute(f'{package} --version')
        print(f'path={path}')
        print(f'version={version}')

    @classmethod
    def python_packages_report(cls):
        """Display all installed packages using pip freeze.

        This method will modify the output and print:

        pypi packages : 'Package Name | Version'
        git repository package: 'Package Name | Repository | Version'
        """
        lines = cls._execute('pip  freeze').split('\n')
        print('# Python Packages')
        for line in lines:
            if 'kytos' in line or 'python-openflow' in line:
                if '==' in line:
                    name, version = line.split('==')
                    print(f'{name:<30} | {version:<30}')
                if line.startswith('-e '):
                    url, name = line.split('#egg=')
                    url = url.replace('-e ', '')
                    repository, hash_number = cls._parse_github_install(url)
                    print(f'{name:<30} | {repository:<30} | {hash_number:<30}')

    @classmethod
    def _parse_github_install(cls, url):
        """Parse the repository url and get the github path and commit hash."""
        pattern = "(github.com[:/].*).git@(.{8})"
        result = re.search(pattern, url)
        if result:
            return result.groups()
        return (url, '')

    @classmethod
    def kytos_environment_report(cls):
        """Display the kytos environment.

        This method shows the path and version of kytos and kytosd.
        After that shows all installed napps.
        """
        print('# Kytos environment')
        cls._print_path_and_version('kytosd')
        cls._print_path_and_version('kytos')
        print('## Installed napps')
        napps = cls._execute('kytos napps list')
        print(napps)

    @classmethod
    def _execute(cls, command):
        """Call a subprocess and return the result."""
        return subprocess.check_output(command, shell=True).decode().strip()
