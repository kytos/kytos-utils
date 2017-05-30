"""kytos - The kytos command line.

You are at the "users" command.

Usage:
       kytos users register
       kytos users -h | --help

Options:

  -h, --help    Show this screen.

Common user subcommands:

  create        Register a new user to upload napps to Napps Server.

"""
import sys

from docopt import docopt

from kytos.cli.commands.users.api import UsersAPI
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
    func = getattr(UsersAPI, subcommand)
    func(args)
