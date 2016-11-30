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
from nappsclient.client import KytosClient
from nappsclient.config import KytosConfig
from nappsclient.cmdline import KytosCmdLine

import getpass
import sys

def main():
    config = KytosConfig()
    if config.napps_uri is None:
        config.save_napps_uri(input("Enter the kytos napps server address: "))

    if config.user is None:
        config.save_user(input("Enter the username: "))

    if config.password is None and config.token is None:
        config.password = getpass.getpass("Enter the password for %s: " % config.user)

    if not config.napps_uri or not config.user or (not config.password and not config.token):
        print("Missing information necessary to connect to napps repository.")
        print("kytos-utils uses theses variables:")
        print("")
        print("NAPPS_API_URI    = Server API endpoing")
        print("NAPPS_USER       = User to authenticate")
        print("NAPPS_PASSWORD   = Password used only to get API token")
        print("")
        print("Use it or configure your config file.")
        print("Aborting...")
        sys.exit()

    client = KytosClient(config.napps_uri, config.debug)
    cmd = KytosCmdLine(client)
    cmd.parse_args()

    if cmd.args.debug:
        client.set_debug()

    # Load global section and token, if token is not found, ask for
    # credentials and get a new token
    if config.token is None:
        print("Token not found in your %s" % config.config_file)
        print("Creating a new one...")
        token = client.request_token(config.user, config.password)
        if token is None:
            print("Error: Could not get token.")
            print("Aborting...")
            sys.exit()

        config.save_token(token)

    client.set_token(config.token)
    cmd.execute()
