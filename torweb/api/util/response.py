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


def error_tb(tb):
    return {
        'message': tb.getErrorMessage(),
        'name': tb.type.__name__
    }

def error(message, name=None):
    return {
        'message': message,
        'name': name
    }

def send_json(response, data):
    data = j.dumps(data).encode('utf8')
    response.write(data)
    response.finish()


class JsonError(resource.Resource):
    
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
        return {'error':
            {
                'name': self.name,
                'message': self.message
            }
        }

    def getChild(self, child, request):
        return self