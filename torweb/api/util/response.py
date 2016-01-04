# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

from .encoder import JSONEncoder, get_encoder
from twisted.web import server

from twisted.web import resource


def encode(func):
    def new_func(*args, **kwargs):
        request = args[-1]
        encoder = None
        if request.requestHeaders.hasHeader('accept'):
            header = request.requestHeaders.getRawHeaders('accept')[0]
            encoder = get_encoder(header)
        if encoder is None:
            error = NotAcceptable()
            return error.render(request)
            args = args[1:]
        else:
            result = func(*args, **kwargs)
            if result != server.NOT_DONE_YET:
                if not type(result) in (str, unicode):
                    result = encoder.dumps(result)
                request.setHeader(b"content-type", encoder.full_type)
            return result

    new_func.__doc__ = func.__doc__
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


def error_exception(exception):
    '''
    Returns an error dict from an exception.
    '''
    return error(exception.__class__.__name__,
                 str(exception))


def send_json(response, data):
    '''
    Write an JSON object to the response stream.
    '''
    data = j.dumps(data).encode('utf8')
    response.write(data)
    response.finish()


class Error(resource.Resource):
    '''
    Resource class which can be returned by :meth:`resource.Resource.getChild`
    and is rendered to a JSON error on GET.
    '''
    message = None
    name = None
    code = 500

    def __init__(self, message=None, name=None):
        resource.Resource.__init__(self)
        if message is not None:
            self.message = message
        if name is not None:
            self.name = name

    @encode
    def render(self, request):
        '''
        Returns the error.
        '''
        request.setResponseCode(self.code)
        return error(self.name, self.message)

    def getChild(self, child, request):
        '''
        Always returns itself so this object can be returned by e.g. the
        "grand-parents".
        '''
        return self

JsonError = Error


class NoResource(Error):
    name = "No Such Resource"
    message = "Sorry. No luck finding that resource."
    code = 404


class UnsuportedMediaTypeError(Error):
    message = "Media Type not supported"
    name = "Unsuported Media Type"
    code = 415


class NotAcceptable(Error):

    name = "Not Acceptable"
    message = "Cannot generate accepted output"
    code = 406

    def render(self, request):
        '''
        Overrides the super method so it doesn't
        try to encode the content.
        '''
        request.setResponseCode(self.code)
        encoder = JSONEncoder(b'application/json', 'charset=utf-8')
        request.setHeader(b"content-type", encoder.full_type)
        return encoder.dumps(error(self.name, self.message))
