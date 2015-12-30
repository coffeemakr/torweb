from twisted.web import resource
from torweb.api.util import response, request
import json
from twisted.web import server
import re
__all__ = ('ConfigurationRoot', 'Configuration')


ERR_CONFIG_NREADY = response.error("Not ready", "Configuration was not set.")


class ConfigurationRoot(resource.Resource):

    configuration = None

    def __init__(self, configuration=None):
        resource.Resource.__init__(self)
        self.configuration = configuration

    def getChild(self, name, request):
        if self.configuration is None:
            return response.JsonError("State Error",
                                      "Configuration not ready.")
        if name in self.configuration.config:
            return Configuration(name=name, configuration=self.configuration)
        return response.JsonError("State Error",
                                  "Configuration doesn't exist.")

    @response.json
    def render_GET(self, request):
        if self.configuration is None:
            return ERR_CONFIG_NREADY
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
            return response.error("Invalid Request",
                                "You sent an invalid request.")
        if self.configuration is None:
            return ERR_CONFIG_NREADY
        value = request.json_content['value']
        if type(value) is bool:
            value = int(value)
            pass
        original_value = self.configuration.config[self.name]
        setattr(self.configuration, self.name, value)
        d = self.configuration.save()

        def on_error(error):
            self.configuration.config[self.name] = original_value
            request.write(json.dumps(response.error_tb(error)).encode('utf-8'))
            request.finish()

        def on_success(*args):
            request.write(self.render_GET(request))
            request.finish()
        d.addCallback(on_success)
        d.addErrback(on_error)
        return server.NOT_DONE_YET
