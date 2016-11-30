# This file is part of kytos-utils.
#
# Copyright (c) 2016 by Kytos Team
#
# Authors:
#    Beraldo Leal <beraldo AT ncc DOT unesp DOT br>
#
# kytos-utils is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kytos-utils is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
import sys
import argparse
import textwrap

class KytosCmdLine():
    def __init__(self, api):
        self.parser = argparse.ArgumentParser(prog='kytos',
                        formatter_class=argparse.RawDescriptionHelpFormatter,
                        description=textwrap.dedent('Kytos Napps client command line.'),
                        epilog=textwrap.dedent('''
                        Environment Variables:

                        NAPPS_API_URI    = Server API endpoing
                        NAPPS_USER       = User to authenticate
                        NAPPS_PASSWORD   = Password used only to get API token

                        Use it or configure your config file.'''))

        self.parser.add_argument('-v', '--version',
                            action='version',
                            version='%(prog)s 0.1.0')

        self.parser.add_argument('-d', '--debug',
                                 action='store_true',
                                 help="Run in debug mode")

        self.parser.set_defaults(func=self.help)
        subparsers = self.parser.add_subparsers(title='commands')

        # napps
        napps = subparsers.add_parser('napps', help='napps help')
        napps_subparsers = napps.add_subparsers(title='napps command' )


        # apps list
        help = "Upload current napp to Kytos repository."
        napps_upload = napps_subparsers.add_parser('upload',
                                                    help=help,
                                                    description="This will upload to Kytos Napps repository a napp on current directory.")
        napps_upload.set_defaults(func=api.upload_napp)

    def help(self, namespace):
        print("Invalid syntax")
        print("Please run kytos --help")
        sys.exit(-1)

    def parse_args(self):
        self.args = self.parser.parse_args()

    def execute(self):
        self.args.func(self.args)
