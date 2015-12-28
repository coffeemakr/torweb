from twisted.web import resource
from torweb.api.util import response, request
import json
from twisted.web import server
import re
__all__ = ('ConfigurationRoot', 'Configuration')


ERROR_CONFIGURATION_NOT_READY = {'error': 'Configuration not ready'}


class ConfigurationRoot(resource.Resource):

    configuration = None

    def __init__(self, configuration=None):
        resource.Resource.__init__(self)
        self.configuration = configuration

    def getChild(self, name, request):
        if self.configuration is None:
            return resource.NoResource("Configuration not ready.")
        if name in self.configuration.config:
            return Configuration(name=name, configuration=self.configuration)
        return resource.NoResource("Configuration doesn't exist.")

    @response.json
    def render_GET(self, request):
        if self.configuration is None:
            return ERROR_CONFIGURATION_NOT_READY
        entries = []
        for name, value in self.configuration.config.items():
            entries.append({"name": name, "value": value})
        return {'objects': entries}


class Configuration(resource.Resource):

    def __init__(self, name, configuration=None):
        if name not in configuration.config:
            raise ValueError("Invalid name")
        self.name = name
        self.configuration = configuration

    @property
    def value(self):
        return self.configuration.config[self.name]

    @property
    def type(self):
        name = type(self.value).__name__
        if name == '_ListWrapper':
            name = 'list'
        elif name == 'unicode':
            name = 'str'
        return name

    @response.json
    def render_GET(self, request):
        return {
            'name': self.name,
            'id': self.name,
            'value': self.value,
            'type': self.type}

    @response.json
    @request.json
    def render_POST(self, request):
        if 'value' not in request.json_content:
            return {'error': 'Invalid request.'}
        if self.configuration is None:
            return ERROR_CONFIGURATION_NOT_READY
        value = request.json_content['value']
        if type(value) is bool:
            # value = int(value)
            pass
        setattr(self.configuration, self.name, value)
        d = self.configuration.save()

        def on_error(error):
            request.write(json.dumps(
                {'error':
                    {
                        'message': error.getErrorMessage(),
                        'name': error.type.__name__
                    }
                 }
            ).encode('utf-8'))
            request.finish()

        def on_success(*args):
            request.write(self.render_GET(request))
            request.finish()
        d.addCallback(on_success)
        d.addErrback(on_error)
        return server.NOT_DONE_YET
