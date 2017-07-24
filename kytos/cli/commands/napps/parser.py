"""kytos - The kytos command line.

You are at the "napps" command.

Usage:
       kytos napps create
       kytos napps upload
       kytos napps delete    <napp>...
       kytos napps list
       kytos napps install   <napp>...
       kytos napps uninstall <napp>...
       kytos napps enable    (all| <napp>...)
       kytos napps disable   (all| <napp>...)
       kytos napps search    <pattern>
       kytos napps -h | --help

Options:

  -h, --help    Show this screen.

Common napps subcommands:

  create        Create a bootstrap NApp structure for development.
  upload        Upload current NApp to Kytos repository.
  delete        Delete NApps from NApps Server.
  list          List all NApps installed into your system.
  install       Install a local or remote NApp into a controller.
  uninstall     Remove a NApp from your controller.
  enable        Enable a installed NApp.
  disable       Disable a NApp.
  search        Search for NApps in NApps Server.

"""
import re
import sys

from docopt import docopt

from kytos.cli.commands.napps.api import NAppsAPI
from kytos.utils.exceptions import KytosException


def parse(argv):
    """Parse cli args."""
    args = docopt(__doc__, argv=argv)
    try:
        call(sys.argv[2], args)
    except KytosException as e:
        print("Error parsing args: {}".format(e))
        exit()


def call(subcommand, args):
    """Call a subcommand passing the args."""
    args['<napp>'] = parse_napps(args['<napp>'])
    func = getattr(NAppsAPI, subcommand)
    func(args)


def parse_napps(napp_args):
    """Return a list of tuples with username, napp_name and version.

    Each napp arg must to have the pattern username/name-version. Version is
    optional, whether no version is found the tuple will be
    ('username', 'name', None).

    e.g:
    If you use ``kytos napps kytos/of_core kytos/of_l2ls-0.1.1`` the returned
    list is [('kytos', 'of_core', None), ('kytos', 'of_l2ls', '0.1.1')].

    Args:
        napp_args (list): NApps from the cli.

    Return:
        list: list of tuples with (username, napp_name, version).

    Raises:
        KytosException: If a NApp has not the form _username/name_.
    """
    if 'all' in napp_args:
        return 'all'

    def parse_napp(arg):
        """Parse one argument."""
        regex = r'([a-zA-Z][a-zA-Z0-9_]{2,})/([a-zA-Z][a-zA-Z0-9_]{2,})-?(.+)?'
        compiled_regex = re.compile(regex)

        matched = compiled_regex.fullmatch(arg)

        if not matched:
            msg = '"{}" NApp has not the form username/napp_name[-version].'
            raise KytosException(msg.format(arg))

        return matched.groups()

    return [parse_napp(arg) for arg in napp_args]
