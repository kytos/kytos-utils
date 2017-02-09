"""Parse arguments of "kytos napps" command."""
from kytos_utils.cli.argparser import ArgSubParser
from kytos_utils.napps.local.api import NAppsAPI
from kytos_utils.napps.local.manager import NAppsManager

__all__ = ('NAppsArgParser',)


mgr = NAppsManager()


class NAppsArgParser(ArgSubParser):
    """Argument parser for _napps_ sub-command."""

    def __init__(self):
        """Name of the sub-command is _napps_."""
        super().__init__('napps')

    def get_parser_args(self):
        """User help."""
        return {'help': 'Network Applications management.'}

    def add_arguments(self, parser):
        """Add subparsers."""
        self._set_subparsers(parser)
        for cls in EnableArgParser, DisableArgParser, ListArgParser:
            self._add_subparser(cls())


class EnableArgParser(ArgSubParser):
    """Argument parser for the _enable_ action."""

    def __init__(self):
        super().__init__('enable')

    def get_parser_args(self):
        return {'help': 'Enable a NApp.'}

    def add_arguments(self, parser):
        parser.add_argument('NApp', help='NApp to be enabled in the format '
                            'napp_author/napp_name')
        parser.set_defaults(func=NAppsAPI.enable)


class DisableArgParser(ArgSubParser):
    """Argument parser for the _disable_ action."""

    def __init__(self):
        super().__init__('disable')

    def get_parser_args(self):
        return {'help': 'Disable a NApp.'}

    def add_arguments(self, parser):
        parser.add_argument('NApp', help='NApp to be disable in the format '
                            'napp_author/napp_name')
        parser.set_defaults(func=NAppsAPI.disable)


class ListArgParser(ArgSubParser):
    """Argument parser for the _disable_ action."""

    def __init__(self):
        super().__init__('list')

    def get_parser_args(self):
        return {'help': 'List all installed NApps.'}

    def add_arguments(self, parser):
        parser.set_defaults(func=NAppsAPI.list)
