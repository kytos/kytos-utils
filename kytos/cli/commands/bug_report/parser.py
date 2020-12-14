"""kytos - The kytos command line.

You are at the "bug-report" command.

Usage:
       kytos bug-report
       kytos bug-report -h | --help

Options:

  -h, --help    Show this screen.
"""

import sys

from docopt import docopt

from kytos.cli.commands.bug_report.api import BugReportAPI
from kytos.utils.exceptions import KytosException


def parse(argv):
    """Parse cli args."""
    args = docopt(__doc__, argv=argv)
    try:
        BugReportAPI.bug_report(args)
    except KytosException as exception:
        print("Error parsing args: {}".format(exception))
        sys.exit(-1)
