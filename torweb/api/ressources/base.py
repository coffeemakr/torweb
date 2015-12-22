# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

from twisted.web import resource
from .error import ResourceError

from torweb.api.util import response

__all__ = ('TorResource', 'TorResourceDetail')


class TorResource(resource.Resource):

    json_list_class = None
    json_detail_class = None

    detail_class = None

    def __init__(self, torstate=None):
        resource.Resource.__init__(self)
        if self.json_list_class is None:
            raise RuntimeError('json_list_class not overriden')
        if self.json_detail_class is None:
            raise RuntimeError('json_detail_class not overriden')
        if self.detail_class is None:
            self.detail_class = TorResourceDetail
        self._torstate = torstate

    def get_list(self):
        '''
        Should return a list of objects
        '''
        raise NotImplementedError()

    def get_by_id(self, ident):
        '''
        Should return a single object
        '''
        raise NotImplementedError()

    @response.json
    def render_GET(self, request):
        error = self.check_torstate()
        result = {}
        if error is None:
            items = []
            for item in self.get_list():
                items.append(self.json_list_class(item).as_dict())
            result['objects'] = items
        result['error'] = error
        return result

    def getChild(self, ident, request):
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
            return resource.NoResource(error)

    def get_torstate(self):
        return self._torstate

    def set_torstate(self, torstate):
        self._torstate = torstate

    torstate = property(get_torstate)

    def check_torstate(self):
        if self._torstate is None:
            return "Tor state is unknown."


class TorResourceDetail(resource.Resource):

    isLeaf = True

    def __init__(self, obj, json_class):
        self.object = obj
        self.json_class = json_class

    @response.json
    def render_GET(self, request):
        return self.json_class(self.object).as_dict()
