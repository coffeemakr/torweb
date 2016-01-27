#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, with_statement

import os

from twisted.web import resource, static, util

from torweb.api.ressources import TorInstances

__all__ = ('TorwebResource', 'ApiResource')


class ApiResource(resource.Resource):
    '''
    RESTful API definition. Currently contains
    only one child:

      * `../tor`: :class:`api.torinstance.TorInstances`.
    '''

    def __init__(self, connections):
        resource.Resource.__init__(self)
        self.putChild('tor', TorInstances(connections))


class TorwebResource(resource.Resource):
    '''
    The root resource for all resources provided by the webserver.
    These are the following:

      * `app`: The webpage for the user interface
      * `api`: The RESTful API (:class:`ApiRessource`).
    '''

    def __init__(self, app_dir, connections):
        resource.Resource.__init__(self)
        self.app_dir = app_dir
        if not os.path.isdir(self.app_dir):
            raise ValueError("{} is not a folder.".format(self.app_dir))
        self.putChild('', util.Redirect('/app'))
        self.putChild('app', static.File(self.app_dir))
        self.putChild('api', ApiResource(connections))
