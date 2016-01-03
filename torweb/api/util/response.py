# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

import json as j
from twisted.web import server

from twisted.web import resource


def json(func):
    def new_func(*args):
        request = args[-1]
        request.responseHeaders.addRawHeader(
            "content-type", "application/json")
        result = func(*args)
        if result != server.NOT_DONE_YET:
            if not type(result) == str:
                result = j.dumps(result).encode('utf8')
        return result
    return new_func


def error(name, message):
    '''
    Returns a serializeable dict containing the error message and the
    error name.
    '''
    return {'error': {'message': message, 'name': name}}


def error_tb(traceback):
    '''
    Returns a error dict containing information about the traceback.
    '''
    return error(traceback.type.__name__,
                 traceback.getErrorMessage())


def send_json(response, data):
    '''
    Write an JSON object to the response stream.
    '''
    data = j.dumps(data).encode('utf8')
    response.write(data)
    response.finish()


class JsonError(resource.Resource):
    '''
    Resource class which can be returned by :meth:`resource.Resource.getChild`
    and is rendered to a JSON error on GET.
    '''
    message = None
    name = None

    def __init__(self, message=None, name=None):
        resource.Resource.__init__(self)
        if message is not None:
            self.message = message
        if name is not None:
            self.name = name

    @json
    def render_GET(self, request):
        '''
        Returns the json error.
        '''
        return error(self.name, self.message)

    def getChild(self, child, request):
        '''
        Always returns itself so this object can be returned by e.g. the
        "grand-parents".
        '''
        return self
