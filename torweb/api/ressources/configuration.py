# -*- coding: utf-8 -*-
'''
This module contains resources to modify the tor configuration as
by RESTful API calls.

 * `GET ../config`: Lists all configuration
   (see :meth:`ConfigurationRoot.render_GET`).
 * `GET ../config/<ConfigId>`: Get details of a single entry
   (see :meth:`Configuration.render_GET`).
 * `POST ../config/<ConfigId>`: Change the value
   (see :meth:`Configuration.render_POST`).

'''
from __future__ import absolute_import, print_function, with_statement

import json
import re

from twisted.web import server

import zope.interface

import txtorcon
from torweb.api.util import response, request
from torweb.api.json import configuration
from .base import TorResource, TorResourceDetail, ITorResource

__all__ = ('ConfigurationRoot', 'Configuration', 'ConfigurationEntry')

ERR_CONFIG_NREADY = response.error("Not ready", "Configuration was not set.")


class ConfigurationEntry(object):
    '''
    Wrapper for configuration values.

    :param config: An instance of :class:`txtorcon.TorConfig`
    :param name: The configuration name.
    '''

    #: The :class:`txtorcon.Toconfig` configuration object
    config = None

    #: The name of the configuration entry
    name = None

    #: The identifier is the same as the name
    id = None

    def __init__(self, name, config):
        self.config = config
        self.name = name
        self.id = name

    @property
    def value(self):
        '''
        The value of the configuration entry.
        '''
        return self.config.config[self.name]

    @property
    def value_type(self):
        '''
        Returns a string of the value type.
        '''
        return self.config.get_type(self.name)

    @property
    def is_list(self):
        '''
        Is :const:`True` if the value is a list.
        '''
        return txtorcon.torconfig.is_list_config_type(self.value_type)


class Configuration(TorResourceDetail):
    '''
    Resource representing a single configuration entry.
    '''

    def update_value(self, value):
        '''
        Updates the value and returns a defered.
        '''
        if isinstance(value, bool):
            value = int(value)
        # TODO: Catch errors here
        setattr(self.object.config, self.object.name, value)
        return self.object.config.save()

    @response.json
    @request.json
    def render_POST(self, request):
        '''
        Renders a POST request.
        This calls :meth:`update_value`.
        '''
        if 'value' not in request.json_content:
            return response.error("Invalid Request",
                                  "You sent an invalid request.")
        if self.object.config is None:
            return ERR_CONFIG_NREADY

        value = request.json_content['value']

        original_value = self.object.value

        defered = self.update_value(value)

        def on_error(error):
            '''
            called on save error.
            '''
            self.object.config.config[self.object.name] = original_value
            request.write(json.dumps(response.error_tb(error)).encode('utf-8'))
            request.finish()

        def on_success(*args):
            '''
            Called on success.
            '''
            print(args)
            request.write(self.render_GET(request))
            request.finish()

        defered.addCallback(on_success)
        defered.addErrback(on_error)
        return server.NOT_DONE_YET


class ConfigurationRoot(TorResource):
    '''
    Resource representing the whole tor process configuration.
    '''

    zope.interface.implements(ITorResource)

    detail_class = Configuration

    json_list_class = configuration.JsonConfigMinimal

    json_detail_class = configuration.JsonConfig

    def get_list(self):
        '''
        Returns a list of configurations.
        '''
        # TODO: better error handling
        if not self._config.configuration:
            raise RuntimeError("Configuration not ready")

        entries = []
        for name in self._config.configuration.config:
            obj = ConfigurationEntry(name, self._config.configuration)
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
        return ConfigurationEntry(ident, self._config.configuration)
