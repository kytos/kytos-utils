"""kytos - The kytos command line.

You are at the "controller" command.

Usage:
       kytos controller start
       kytos controller stop
       kytos controller status
       kytos controller -h | --help

Options:

  -h, --help    Show this screen.

Common controller sub commands:

  start        Run kytos controller.
  stop         Stop kytos controller.
  status       Display the kytos controller status.

"""
import sys

from docopt import docopt

from kytos.cli.commands.controller.api import ControllerAPI
from kytos.utils.exceptions import KytosException


def parse(argv):
    """Parse cli args."""
    docopt(__doc__, argv=argv)
    try:
        call(sys.argv[2])
    except KytosException as exception:
        print("Error parsing args: {}".format(exception))
        exit()


def call(subcommand):
    """Call a subcommand."""
    func = getattr(ControllerAPI, subcommand)
    func()
