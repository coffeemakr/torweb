#!/usr/bin/env python
# coding=utf-8
from __future__ import absolute_import, with_statement

import json
import sys
from io import open

from zope import interface


class IConfigurationEntry(interface.Interface):
    def load(self, value):
        '''
        Parse the value and return the parsed value.
        If the value doesn't match the required criterias a
        ValueError is raised.
        '''

    def get_default(self):
        '''
        Returns the default value. Normally None.
        '''


class ConfigEntry(object):
    '''
    Base class for configuration entries.
    '''
    interface.implements(IConfigurationEntry)

    #: The default value
    default_value = None
    #: A tuple of types or a single type which are checked in :meth:`load`
    instanceof = None

    def __init__(self, instanceof=None, default_value=None):

        if instanceof is not None:
            self.instanceof = instanceof

        if default_value is not None:
            self.default_value = default_value

    def load(self, value):
        '''
        This method checks if the given value is an instance of
        :attr:`instanceof`.
        '''
        if self.instanceof is not None and \
           not isinstance(value, self.instanceof):
            msg = "Invalid type: {} - expected {}"
            msg = msg.format(type(value), self.instanceof)
            raise ValueError(msg)
        return value

    def get_default(self):
        '''
        Returns the default value for this configuration entry.
        By default it returns :const:`None` (:attr:`default_value`)
        '''
        return self.default_value


class IntegerEntry(ConfigEntry):
    '''
    Integer configuration entries.
    '''
    instanceof = int


class DictEntry(ConfigEntry):
    '''
    Dictionary configuration entries.
    '''
    instanceof = dict

    entries = None

    def __init__(self, entries=None):
        super(DictEntry, self).__init__(default_value=[])
        if entries is not None:
            self.entries = entries
        if self.entries is None:
            raise RuntimeError("entries have to be set")

    def load(self, value):
        value = super(DictEntry, self).load(value)
        new_value = self.get_default()
        for name, entry_value in value.items():
            if name not in self.entries:
                # TODO: better error message / exception
                raise ValueError("Invalid entry: " + repr(name))
            new_value[name] = self.entries[name].load(entry_value)
        return new_value

    def get_default(self):
        defaults = {}
        for name, entry in self.entries.items():
            defaults[name] = entry.get_default()
        return defaults


class ListEntry(ConfigEntry):
    '''
    List configuration entries.
    '''
    instanceof = list

    def __init__(self, entry_type):
        super(ListEntry, self).__init__(default_value=[])
        self._entry_type = entry_type

    def load(self, value):
        value = super(ListEntry, self).load(value)
        for index, item in enumerate(value):
            value[index] = self._entry_type.load(item)
        return value


class StringEntry(ConfigEntry):
    '''
    String configuration entries.
    '''
    default_value = None

    def load(self, value):
        if sys.version_info[0] == 2:
            # legacy
            if isinstance(value, str):
                value = value.decode('utf-8')
            elif not isinstance(value, unicode):
                msg = "Invalid string type: {}"
                msg = msg.format(type(value))
                raise ValueError(msg)
        else:
            if isinstance(value, bytes):
                value = value.decode('utf-8')
            elif not isinstance(value, str):
                msg = "Invalid string type: {}"
                msg = msg.format(type(value))
                raise ValueError(msg)
        return value


class BooleanEntry(ConfigEntry):
    '''
    Boolean configuration entries.
    '''
    instanceof = (str, bool, int)

    def load(self, value):
        value = super(BooleanEntry, self).load(value)
        if isinstance(value, str):
            value = value.lower()
            if value in ('false', '0'):
                value = False
            elif value in ('true', '1'):
                value = True
            else:
                msg = "String value for Boolean not understood: %r" % value
                raise ValueError(msg)
        elif isinstance(value, int):
            if value == 1:
                value = True
            elif value == 0:
                value = False
            else:
                msg = "Integer value for Boolean not understood: {}"
                msg = msg.format(value)
                raise ValueError("value")
        return value


class PermissionsEntry(StringEntry):
    '''
    Permission configuration entries.
    '''
    def load(self, value):
        value = super(PermissionsEntry, self).load(value)
        if len(value) > 3:
            raise ValueError("Expected three octal digits")
        value = int(value, 8)
        return value


class Configuration(object):

    root_entry = None

    def __init__(self, configfile=None, configuration=None, root_entry=None):
        if root_entry is not None:
            self.root_entry = root_entry
        self.root_entry = IConfigurationEntry(self.root_entry)

        self._config = None
        if configfile is not None:
            self.read_file(configfile)
        else:
            self.clear()

    def read_raw_configuration(self, raw_config):
        self._config = self.root_entry.load(raw_config)

    def clear(self):
        self._config = self.root_entry.get_default()

    def read_file(self, path):
        with open(path, 'rb') as configfile:
            raw_config = json.load(configfile)
        self.read_raw_configuration(raw_config)

    @property
    def value(self):
        return self._config
