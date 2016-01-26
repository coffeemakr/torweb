#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, with_statement

import json
import os

from twisted.web import resource, static, util

from torweb.api.ressources import TorInstances
from torweb.error import ConfigurationError

__all__ = ('TorwebResource', 'ApiResource')


class TorwebResource(resource.Resource):
    '''
    The root resource for all resources provided by the webserver.
    These are the following:

      * `app`: The webpage for the user interface
      * `api`: The RESTful API (:class:`ApiRessource`).
    '''

    def __init__(self, basedir):
        resource.Resource.__init__(self)
        self.basedir = basedir

        config = self._read_config('torweb.json')

        self.putChild('', util.Redirect('/app'))
        self.putChild('app', static.File(self.basedir))
        self.putChild('api', ApiResource(config))

    def _read_config(self, filename):
        '''
        Read the configuration file.
        :param filename: The filename relative to the basedir or
                         an absolute path.
        '''
        if not os.path.isabs(filename):
            filename = os.path.join(self.basedir, filename)
        with open(filename, 'rb') as configfile:
            try:
                config = json.load(configfile)
            except json.error as why:
                raise ConfigurationError("Invalid JSON: " + str(why))
        return config


class ApiResource(resource.Resource):
    '''
    RESTful API definition. Currently contains
    only one child:

      * `../tor`: :class:`api.torinstance.TorInstances`.
    '''

    def __init__(self, config):
        resource.Resource.__init__(self)
        self.putChild('tor', TorInstances(config))
