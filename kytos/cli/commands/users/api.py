"""Translate cli commands to non-cli code."""
import logging

from kytos.utils.users import UsersManager

LOG = logging.getLogger(__name__)


class UsersAPI:
    """An API for the command-line interface.

    Use the config file only for required options. Static methods are called
    by the parser and they instantiate an object of this class to fulfill the
    request.
    """

    user_manager = UsersManager()

    @classmethod
    def register(cls, args):  # pylint: disable=unused-argument
        """Create a new user and register it on the Napps server."""
        result = cls.user_manager.register()
        print(result)
