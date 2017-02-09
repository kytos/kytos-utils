"""Base classes to ease the creation of argument parsers."""
from abc import abstractmethod
from argparse import ArgumentParser


class ArgParser(ArgumentParser):
    """Ease adding subparsers by using ArgSubParser."""

    def __init__(self, *args, **kwargs):
        """Same parameters as :class:`ArgumentParser`."""
        super().__init__(*args, **kwargs)
        self.__kytos_subparsers = None
        self.__kytos_subparsers_args = {'help': 'sub-command help'}

    def set_subparsers_args(self, **kwargs):
        """(Named) parameters for :meth:`ArgumentParser.add_subparsers`."""
        self.__kytos_subparsers_args = kwargs

    def add_subparser(self, subparser):
        """Add a subparser of type :class:`ArgSubParser`.

        Args:
            subparser (ArgSubParser): Sub-command parser to be added.
        """
        if self.__kytos_subparsers is None:
            kwargs = self.__kytos_subparsers_args
            self.__kytos_subparsers = self.add_subparsers(**kwargs)
        subparsers = self.__kytos_subparsers

        # Get command and add_parser parameters
        command = subparser.command
        kwargs = subparser.get_parser_args()
        parser = subparsers.add_parser(command, **kwargs)
        subparser.add_arguments(parser)


class ArgSubParser:
    """Child classes can be easily added as subparsers."""

    def __init__(self, command):
        """Require a command name to be used right after _kytos_ in cli."""
        self.command = command
        self._subparsers = None

    @abstractmethod
    def get_parser_args(self):
        """Return arguments for adding this parser as a subparser.

        The parameters are the same as those in ArgumentParser constructor. To
        keep it simple, they should be returned as a dictionary. It is ok to
        return an empty dict, but the _help_ parameter is useful for the user
        to see what each command does. The example below is for the _napp_
        command.

        Return:
            dict: Parameters as in ArgumenParser constructor.

        Example:
            .. code-block::

                return {'help': 'Network Applications management.'}
        """
        pass

    @abstractmethod
    def add_arguments(self, parser):
        """Add all arguments to the parser. You may call other parser methods.

        Args:
            parser (argparse.ArgumentParser): Parser for :attr:`command`.
        """
        pass

    def _set_subparsers(self, parser):
        """Generate a subparser from ``parser``.

        Use parameters from :meth:`_get_subparsers_args`. If you want to add
        a subparser, call this method before, in the overriden
        :meth:`add_arguments`.

        Args:
            parser (argparse.ArgumentParser): Parser to add subparsers.
        """
        kwargs = self._get_subparsers_args()
        self._subparsers = parser.add_subparsers(**kwargs)

    @staticmethod
    def _get_subparsers_args():
        """Return parameters for subparsers creation.

        Return:
            dict: Parameters of :meth:`ArgumentParser.add_subparsers`. Default
                is ``{'help': 'sub-command help'}``.
        """
        return {'help': 'sub-command help'}

    def _add_subparser(self, subparser):
        """Add a subparser.

        Args:
            subparser (ArgSubParser): Subparser to be added.
        """
        command = subparser.command
        kwargs = subparser.get_parser_args()
        parser = self._subparsers.add_parser(command, **kwargs)
        subparser.add_arguments(parser)
