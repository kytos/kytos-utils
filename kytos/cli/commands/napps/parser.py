"""kytos - The kytos command line.

You are at the "napps" command.

Usage:
       kytos napps create [--meta]
       kytos napps prepare
       kytos napps upload
       kytos napps delete    <napp>...
       kytos napps list
       kytos napps install   <napp>...
       kytos napps uninstall <napp>...
       kytos napps enable    (all| <napp>...)
       kytos napps disable   (all| <napp>...)
       kytos napps reload    (all| <napp>...)
       kytos napps search    <pattern>
       kytos napps -h | --help

Options:

  -h, --help    Show this screen.

Common napps subcommands:

  create        Create a bootstrap NApp structure for development.
  prepare       Prepare NApp to be uploaded (called by "upload").
  upload        Upload current NApp to Kytos repository.
  delete        Delete NApps from NApps Server.
  list          List all NApps installed into your system.
  install       Install a local or remote NApp into a controller.
  uninstall     Remove a NApp from your controller.
  enable        Enable a installed NApp.
  disable       Disable a NApp.
  reload        Reload NApps code.
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
    except KytosException as exception:
        print("Error parsing args: {}".format(exception))
        exit()


def call(subcommand, args):
    """Call a subcommand passing the args."""
    args['<napp>'] = parse_napps(args['<napp>'])
    func = getattr(NAppsAPI, subcommand)
    func(args)


def parse_napps(napp_ids):
    """Return a list of tuples with username, napp_name and version.

    napp_ids elements are of the form username/name[:version]
    (version is optional). If no version is found, it will be None.

    If napp_ids is equal to 'all', this string will be returned.

    Args:
        napp_ids (list): NApps from the cli.

    Return:
        list: list of tuples with (username, napp_name, version).

    Raises:
        KytosException: If a NApp has not the form _username/name_.

    """
    if 'all' in napp_ids:
        return 'all'

    return [parse_napp(napp_id) for napp_id in napp_ids]


def parse_napp(napp_id):
    """Convert a napp_id in tuple with username, napp name and version.

    Args:
        napp_id: String with the form 'username/napp[:version]' (version is
                  optional). If no version is found, it will be None.

    Returns:
        tuple: A tuple with (username, napp, version)

    Raises:
        KytosException: If a NApp has not the form _username/name_.

    """
    # `napp_id` regex, composed by two mandatory parts (username, napp_name)
    # and one optional (version).
    # username and napp_name need to start with a letter, are composed of
    # letters, numbers and uderscores and must have at least three characters.
    # They are separated by a colon.
    # version is optional and can take any format. Is is separated by a hyphen,
    # if a version is defined.
    regex = r'([a-zA-Z][a-zA-Z0-9_]{2,})/([a-zA-Z][a-zA-Z0-9_]{2,}):?(.+)?'
    compiled_regex = re.compile(regex)

    matched = compiled_regex.fullmatch(napp_id)

    if not matched:
        msg = '"{}" NApp has not the form username/napp_name[:version].'
        raise KytosException(msg.format(napp_id))

    return matched.groups()
