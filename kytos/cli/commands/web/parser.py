"""kytos - The kytos command line.

You are at the "web" command.

Usage:
       kytos web update
       kytos web update <version>

Options:

  -h, --help    Show this screen.

Common web subcommands:

  update        Update the web-ui with the latest version

"""
import sys

from docopt import docopt

from kytos.cli.commands.web.api import WebAPI
from kytos.utils.exceptions import KytosException


def parse(argv):
    """Parse cli args."""
    args = docopt(__doc__, argv=argv)
    try:
        call(sys.argv[2], args)
    except KytosException as exception:
        print("Error parsing args: {}".format(exception))
        exit()


def call(subcommand, args):  # pylint: disable=unused-argument
    """Call a subcommand passing the args."""
    func = getattr(WebAPI, subcommand)
    func(args)
