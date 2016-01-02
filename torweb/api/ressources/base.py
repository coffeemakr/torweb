# -*- coding: utf-8 -*-
'''
This module provides classes for resources which depend on a tor instance.
'''
from __future__ import absolute_import, print_function, with_statement

from twisted.web import resource
from .instanceconfig import TorInstanceConfig
from torweb.api.util import response


__all__ = ('TorResource', 'TorResourceDetail')


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

    needs_state = True

    def __init__(self, config=None):
        resource.Resource.__init__(self)

        if config is None:
            config = TorInstanceConfig()
        elif not isinstance(config, TorInstanceConfig):
            raise TypeError("Expected TorInstanceConfig")
        self._config = config
        self._check_class_attributes()

    def _check_class_attributes(self):
        if self.json_list_class is None:
            raise RuntimeError('json_list_class not overriden')
        if self.json_detail_class is None:
            raise RuntimeError('json_detail_class not overriden')
        if self.detail_class is None:
            self.detail_class = TorResourceDetail

    def get_list(self):
        '''
        Should return a list of objects
        '''
        raise NotImplementedError()

    def get_by_id(self, ident):
        '''
        Should return a single object.

        :param ident: The identifier
        '''
        raise NotImplementedError()

    @response.json
    def render_GET(self, request):
        '''
        Renders a json list of all children.
        '''
        error = self.check_torstate()
        result = {}
        if error is None:
            items = []
            for item in self.get_list():
                items.append(self.json_list_class(item).as_dict())
            result['objects'] = items
        else:
            result = response.error('Not ready', error)
        return result

    def getChild(self, ident, request):
        '''
        Get the resource to render and/or manupilute a single child resource.

        If :attr:`detail_class` is set an object of this class is returned.
        Otherwise a :class:`TorResourceDetail` instance is created.

        This method calls :meth:`get_by_id` with the url parameter as
        identifier.
        '''
        error = self.check_torstate()
        if error is None:
            if not ident:
                return resource.NoResource("Empty identifier.")
            try:
                item = self.get_by_id(ident)
            except ValueError:
                return resource.NoResource("Invalid identifier.")
            if item is None:
                return resource.NoResource("Resource doesn't exist.")
            return self.detail_class(item, self.json_detail_class)
        else:
            return response.JsonError("Not ready", error)

    def get_torstate(self):
        return self._config.state

    def set_torstate(self, state):
        self._config.state = state

    torstate = property(get_torstate, set_torstate)

    def check_torstate(self):
        if self._config.state is None:
            return "Tor state is unknown."

    @property
    def configuration(self):
        return self._config.configuration


class CallOnRender(object):

    def __init__(self, method):
        self.method = method

    @response.json
    def __call__(self, request):
        self.object[self.method]()
        return {}


class TorResourceDetail(resource.Resource):

    isLeaf = True

    def __init__(self, obj, json_class):
        self.object = obj
        self.json_class = json_class

    @response.json
    def render_GET(self, request):
        return self.json_class(self.object).as_dict()
