
from .encoder import JSONEncoder, get_encoder
from .response import UnsuportedMediaTypeError


def decode(func):
    def new_func(self, request, *args):
        encoder = None
        if request.requestHeaders.hasHeader('content-type'):
            header = request.requestHeaders.getRawHeaders('content-type')[0]
            encoder = get_encoder(header)
        if encoder is None:
            error = UnsuportedMediaTypeError()
            return error.render(request)
        else:
            # TODO: Error handling
            content = request.content.getvalue()
            request.json_content = encoder.loads(content)
            return func(self, request, *args)
    new_func.__doc__ = func.__doc__
    return new_func

json = decode
