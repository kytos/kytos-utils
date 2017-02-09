"""kytos - The kytos command line.

You are at the "napps" command.

Usage:
       kytos napps <subcommand> [<napp>...]
       kytos napps -h | --help

Options:

  -h, --help    Show this screen.

Common napps subcommands:

  create        Create a bootstrap NApp structure for development.
  upload        Upload current NApp to Kytos repository.
  list          List all NApps installed into your system.
  install       Install a NApp into a controller.
  uninstall     Remove a NApp from your controller.
  enable        Enable a installed NApp.
  disable       Disable a NApp.

"""
from docopt import docopt
from kytos.utils.exceptions import KytosException
from kytos.utils.napps import NappsManager

nm = NappsManager()

def parse(argv):
  args = docopt(__doc__, argv=argv)
  try:
    call(args['<subcommand>'], args['<napp>'])
  except KytosException as e:
    print("Error parsing args: {}".format(e))
    exit(__doc__)

def call(subcommand, args):
  func = getattr(NappsManager, subcommand)
  func(args)
