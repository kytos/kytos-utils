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
    """Return a list of username and napp_name from the napp list argument.

    The expected format of a NApp is napp_username/napp_name.

    Args:
        napp_args (list): NApps from the cli.

    Return:
        list: tuples (username, napp_name).

    Raises:
        KytosException: If a NApp has not the form _username/name_.
    """
    if 'all' in napp_args:
        return 'all'

    def parse_napp(arg):
        """Parse one argument."""
        napp = arg.split('/')
        size_is_valid = len(napp) == 2 and napp[0] and napp[1]
        if not size_is_valid:
            msg = '"{}" NApp has not the form username/napp_name.'.format(arg)
            raise KytosException(msg)
        return tuple(napp)

    return [parse_napp(arg) for arg in napp_args]
