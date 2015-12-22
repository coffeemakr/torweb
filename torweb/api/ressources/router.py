# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

from twisted.web import resource
from .base import TorResource
from torweb.api.util import response
from torweb.api.json import JsonRouter

__all__ = ('RouterRoot', 'Router')


class RouterRoot(TorResource):

    def getChild(self, name, request):
        if not name:
            return resource.NoResource("No List available.")
        try:
            name = '$' + name
            return Router(self.torstate.routers[name])
        except KeyError:
            return resource.NoResource("No such router.")


class Router(resource.Resource):

    isLeaf = True

    def __init__(self, router):
        resource.Resource.__init__(self)
        self.router = router

    @response.json
    def render_GET(self, request):
        return JsonRouter(self.router).json()
