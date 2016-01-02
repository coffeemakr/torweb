# -*- coding: utf-8 -*-

from twisted.web import resource
from torweb.api.util import response, request
import json
from twisted.web import server
import re
from .instanceconfig import TorInstanceConfig
from torweb.api.json.configuration import JsonConfig, JsonConfigMinimal
from .base import TorResource, TorResourceDetail

__all__ = ('ConfigurationRoot', 'Configuration')

ERR_CONFIG_NREADY = response.error("Not ready", "Configuration was not set.")


class ConfigObject(object):

    def __init__(self, name, config):
        self.config = config
        self.value = config.config[name]
        self.name = name
        self.id = name

    @property
    def type(self):
        name = type(self.value).__name__
        if name == '_ListWrapper':
            name = 'list'
        elif name == 'unicode':
            name = 'str'
        return name


class Configuration(TorResourceDetail):

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


class ConfigurationRoot(TorResource):

    detail_class = Configuration

    json_list_class = JsonConfigMinimal

    json_detail_class = JsonConfig

    def get_list(self):
        # TODO: check if configuration is ready
        entries = []
        for name, value in self._config.configuration.config.items():
            obj = ConfigObject(name, self._config.configuration)
            entries.append(obj)
        return entries

    def get_by_id(self, ident):
        '''
        Should return a single object.

        :param ident: The identifier
        '''
        ident = str(ident)
        if ident not in self._config.configuration.config:
            return None
        value = self._config.configuration.config[ident]
        return ConfigObject(ident, self._config.configuration)
