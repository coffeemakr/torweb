# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

from twisted.web import resource
from .base import TorResource, TorResourceDetail
from torweb.api.util import response
from torweb.api.json import JsonStream

__all__ = ('StreamRoot',)


class Stream(TorResourceDetail):

    @response.json
    def render_DELETE(self, request):
        print("DELETE STREAM", self.object.close())
        return {}


class StreamRoot(TorResource):

    json_list_class = JsonStream
    json_detail_class = JsonStream

    detail_class = Stream

    def get_by_id(self, ident):
        ident = int(ident)
        if ident not in self.torstate.streams:
            return None
        return self.torstate.streams[ident]

    def get_list(self):
        return self.torstate.streams.values()
