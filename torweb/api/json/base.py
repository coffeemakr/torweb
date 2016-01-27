# -*- coding: utf-8 -*-
'''
Base classes to encode classes.
'''
from __future__ import absolute_import, print_function, with_statement

import zope.interface

__all__ = ('JsonObjectWrapper', 'IJSONSerializable')


class IJSONSerializable(zope.interface.Interface):
    '''
    Interface for all serializeable objects
    '''

    def as_dict(self):
        '''
        Returns the objects as a serializable dictionary
        '''


class JsonObjectWrapper(object):
    '''
    Base class for serializeable object wrappers.
    '''

    zope.interface.implements(IJSONSerializable)

    #: List or tuple of tuples or a dictionary with two values:
    #: The old and the new attribute name.
    rename = ()

    #: All names of attributes to copy into the json dictionary
    attributes = ()

    def __init__(self, obj):
        self.object = obj
        self._rename = dict(self.rename)

    def as_dict(self):
        '''
        Returns a dictionary of all :attr:`attributes`.
        '''
        result = {}
        for attr in self.attributes:
            value = getattr(self.object, attr)
            if attr in self._rename:
                attr = self._rename[attr]
            result[attr] = value
        return result
