# -*- coding: utf-8 -*-
'''
This module provides classes for resources which depend on a tor instance.
'''
from __future__ import absolute_import, print_function, with_statement


import zope.interface

from twisted.web import resource

from torweb.api.json.base import IJSONSerializable
from torweb.api.util import response

from .instanceconfig import TorInstanceConfig

__all__ = ('ITorResource', 'TorResource', 'TorResourceDetail')


class ITorResource(resource.IResource):
    '''
    Tor resource
    '''

    json_list_class = zope.interface.Attribute(
        "Class to serialize an object for lists.")

    json_detail_class = zope.interface.Attribute(
        "Class to serialize the object with the max. verbosity.")

    def get_list(self):
        '''
        Should return a list of objects
        '''

    def get_by_id(self, ident):
        '''
        Should return a single object.

        :param ident: The identifier
        '''

    def render_GET(self, request):
        '''
        Renders a json list of all children.
        '''


class TorResource(resource.Resource):
    '''
    Base class for resources bound to a tor instance.
    '''

    #: Class to serialize an object for lists.
    json_list_class = None

    #: Class to serialize the object with the max. verbosity.
    json_detail_class = None

    #: Class for child resources. This should be an subclass of
    #: :class:`TorResourceDetail` or :class:`resource.Resource` which takes
    #: the same constructor parameters as :class:`TorResourceDetail`.
    detail_class = None

    def __init__(self, config=None):
        resource.Resource.__init__(self)

        if config is None:
            config = TorInstanceConfig()
        elif not isinstance(config, TorInstanceConfig):
            raise TypeError("Expected TorInstanceConfig")
        self._config = config

        self._json_list_class = self.json_list_class
        self._json_detail_class = self.json_detail_class

        if self.detail_class is None:
            self.detail_class = TorResourceDetail
        self.detail_class = self.detail_class

    @response.encode
    def render_GET(self, request):
        '''
        Renders a json list of all children.
        '''
        if self._config.state is None:
            return response.error('Not ready', 'State unknown.')
        result = {}
        items = []
        try:
            for item in ITorResource(self).get_list():
                items.append(self.json_list_class(item))
        except RuntimeError as why:
            result = response.error_exception(why)
        else:
            result['objects'] = items
        return result

    def getChild(self, ident, request):
        '''
        Get the resource to render and/or manupilute a single child resource.

        If :attr:`detail_class` is set an object of this class is returned.
        Otherwise a :class:`TorResourceDetail` instance is created.

        This method calls :meth:`get_by_id` with the url parameter as
        identifier.
        '''
        if self._config.state is not None:
            if not ident:
                return response.NoResource("Empty identifier.")
            try:
                item = ITorResource(self).get_by_id(ident)
            except ValueError:
                return response.NoResource("Invalid identifier.")
            if item is None:
                return response.NoResource("Resource doesn't exist.")
            return self.detail_class(item, self.json_detail_class)
        else:
            return response.Error("Not ready", "State unknown.")


class TorResourceDetail(resource.Resource):
    '''
    Base class for all resource details.
    Objects of this class are returned by :meth:`TorResource.getChil` by
    default.
    '''

    #: Is leaf because detail resources cannot have children.
    isLeaf = True

    #: The object which contains all information
    object = None

    #: The class which can be used to serialize the object.
    json_class = None

    def __init__(self, obj, json_class):
        '''
        :param obj: Sets :attr:`object`
        :param json_class: A class which can serialize the :attr:`object`.
        '''
        resource.Resource.__init__(self)
        self.object = obj
        self.json_class = json_class

    @response.encode
    def render_GET(self, request):
        '''
        Uses :attr:`json_class` to serialize :attr:`object`.
        '''
        return self.json_class(self.object).as_dict()
