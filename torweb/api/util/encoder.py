
import json as j

import zope.interface

__all__ = ('IContentEncoder', 'JSONEncoder', 'ENCODER_BY_TYPE')


class IContentEncoder(zope.interface.Interface):
    types = zope.interface.Attribute("List of mime types supported "
                                     "by this encoder")

    def loads(self, content):
        '''
        Returns a decoded dictionary
        '''

    def dumps(self, content):
        '''
        Returns an encoded string
        '''


class BaseEncoder(object):
    '''
    Base class for encoders
    '''

    def __init__(self, full_type, parameters=None):

        self.full_type = full_type
        self.parameters = parameters

    @property
    def sub_type(self):
        return self.full_type.split('/')[1]

    @property
    def top_type(self):
        return self.full_type.split('/')[0]


class JSONEncoder(BaseEncoder):

    zope.interface.implements(IContentEncoder)

    types = ('application/json',)

    def loads(self, content):
        content = content.decode('utf-8')
        return j.loads(content)

    def dumps(self, content):
        return j.dumps(content).encode('utf-8')


_HTML_WRAPPER = '''
<html>
<head>
    <title>Resource View</title>
    <link rel="stylesheet"
    href="/app/components/bootstrap/dist/css/bootstrap.css">
    <link rel="stylesheet" href="/app/css/app.css">
</head>
<body>
<main class="container">
    <h1>Resource View</h1>
    <h2>JSON Dump</h2>
    <pre>{0}</pre>
</main>
<body>
</html>
'''

_HTML_ERROR_WRAPPER = '''
<html>
<head>
    <title>Resource ERROR</title>
    <link rel="stylesheet"
    href="/app/components/bootstrap/dist/css/bootstrap.css">
    <link rel="stylesheet" href="/app/css/app.css">
</head>
<body>
<main class="container">
    <div role="alert", class="alert alert-danger">
    <h1>{name}</h1>
    <h2>{message}</h2>
    </div>
</main>
<body>
</html>
'''


class HTML5Encoder(BaseEncoder):

    zope.interface.implements(IContentEncoder)

    types = ('text/html',)

    def loads(self, content):
        # FIXME: Implement a way to tell if encoding is supported
        raise RuntimeError("Only for dump! .. and fun :)")

    def dumps(self, content):
        if 'error' in content and 'message' in content['error'] and \
                'name' in content['error']:
            # we assume it an error
            name = content['error']['name']
            message = content['error']['message']
            return _HTML_ERROR_WRAPPER.format(name=name, message=message)

        data = j.dumps(content, separators=(',', ': '),
                       indent=4).encode('utf-8')
        return _HTML_WRAPPER.format(data)


ENCODER = [JSONEncoder, HTML5Encoder]
ENCODER_BY_TYPE = {}


def _init_encoder():
    for encoder in ENCODER:
        for type_ in encoder.types:
            ENCODER_BY_TYPE[type_] = encoder

_init_encoder()


def get_encoder(raw_header, default='application/json'):
    '''
    :param raw_header: The header containing the type information
    :param default: The default type for wildcards
    :returns: IContentEncoder object
    '''
    encoder_class = None
    types = raw_header.split(',')
    for type_ in types:
        parameters = None
        if ';' in type_:
            type_, parameters = type_.split(';', 1)
        type_ = type_.strip()
        if type_ == '*/*' and default is not None:
            type_ = default
        if type_ in ENCODER_BY_TYPE:
            encoder_class = ENCODER_BY_TYPE[type_]
            break

    if encoder_class is not None:
        return IContentEncoder(encoder_class(type_, parameters))
    return None
