"""Translate cli commands to non-cli code."""
import logging
from urllib.error import HTTPError, URLError

import requests

from kytos.utils.config import KytosConfig

LOG = logging.getLogger(__name__)


class WebAPI:  # pylint: disable=too-few-public-methods
    """An API for the command-line interface."""

    @classmethod
    def update(cls, args):
        """Call the method to update the Web UI."""
        kytos_api = KytosConfig().config.get('kytos', 'api')
        url = f"{kytos_api}api/kytos/core/web/update"
        version = args["<version>"]
        if version:
            url += f"/{version}"

        try:
            result = requests.post(url)
        except(HTTPError, URLError, requests.exceptions.ConnectionError):
            LOG.error("Can't connect to server: %s", kytos_api)
            return

        if result.status_code != 200:
            LOG.info("Error while updating web ui: %s", result.content)
        else:
            LOG.info("Web UI updated.")
