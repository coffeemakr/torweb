# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

from zope.interface import implements

from torweb.api.json.stream import JsonStream
from torweb.api.util import response

from .base import ITorResource, TorResource, TorResourceDetail

__all__ = ('StreamRoot',)


class Stream(TorResourceDetail):
    '''
    Stream resource which allows rendering and closing of a stream.
    '''
    @response.encode
    def render_DELETE(self, request):
        '''
        Closes the stream.
        '''
        print("DELETE STREAM", self.object.close())
        return {}


class StreamRoot(TorResource):
    '''
    Stream API base. This class renders lists and implements :meth:`getChild`
    to return :class:`Stream` objects for details and modifications.
    '''

    implements(ITorResource)

    #: The json wrapper for lists.
    json_list_class = JsonStream

    #: The json wrapper for details
    json_detail_class = JsonStream

    #: :class:`Stream` implements the details of a single stream.
    detail_class = Stream

    def get_by_id(self, ident):
        '''
        Returns a stream by its identifier.
        '''
        ident = int(ident)
        if ident not in self._config.state.streams:
            return None
        return self._config.state.streams[ident]

    def get_list(self):
        return self._config.state.streams.values()
