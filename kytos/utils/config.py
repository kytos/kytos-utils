"""Manage config file."""
import logging
from configparser import ConfigParser
from os import path

log = logging.getLogger('kytos.config')


class Config:
    """Manage the config file with automatic saving.

    This class works like a shortcut to several :class:`ConfigParser`
    operations. You don't have to worry about saving the file or creating new
    sections if they don't exist yet. There's also an option to warn the user
    if a configuration is not found a default value is created. For any method
    not implemented here, use the attributes directly.

    Note:
        If you modify the config using the attributes directly, you must call
        :meth:`save` to save the modifications.

    Attributes:
        config (ConfigParser): The whole config, result of
            :meth:`ConfigParser.read`
        section (configparser.SectionProxy): The config section or None if not
            set yet.
    """

    FILE = path.expanduser('~/.kytosrc')

    def __init__(self, section=None):
        """Optionally set the desired section.

        Args:
            section (str, optional): Section to use. If not specified, call
                :meth:`set_section` later.
        """
        self.config = ConfigParser()
        if path.exists(self.FILE):
            self.config.read(self.FILE)
        self.set_section(section)

    def set_section(self, section):
        """Set the desired section to use values from. Create if needed.

        Args:
            section (str): Section to use.
        """
        if section not in self.config:
            self.config[section] = {}
        self.section = self.config[section]

    def has(self, key):
        """Whether the section has a key."""
        return key in self.section

    def get(self, key):
        """Return key's value or exception if not found.

        To avoid exception, use :meth:`has`. Requires a section already set.

        Raises:
            KeyError: If there's no such key.
        """
        return self.section[key]

    def setdefault(self, key, default, warn=False):
        """If a key is not found, set the default value and return it.

        This method works like :meth:`dict.setdefault`. To warn a user that a
        default value has been crated, use ``warn=True``.

        Args:
            key (str): Value's key.
            default (str, function): Default value to set and return if key is
                not found. The value string or a function that returns it.
            warn (bool): Whether or not to warn the user when the default value
                is set (and created in the config file).
        """
        if key in self.section:
            return self.section[key]
        else:
            return self.set(key, default, warn)

    def set(self, key, value, warn=False):
        """Set a value for a key and updates the config file.

        Args:
            key (str): Value's key.
            value (str, function): Default value to set and return if key is
                not found. The value string or a function that returns it.
            warn (bool): Whether or not to warn the user when the default value
                is set (and created in the config file).
        """
        _value = value() if callable(value) else value
        self.section[key] = _value
        self.save()
        if warn:
            log.warning('Configuration "%s" not found in %s and the value "%s"'
                        ' was added.', key, self.FILE, _value)
        # If we return _value, interpolation is lost
        return self.section[key]

    def save(self):
        """Save the file. No need to save after ``set`` or ``setdefault``."""
        with open(self.FILE, 'w') as f:
            self.config.write(f)
