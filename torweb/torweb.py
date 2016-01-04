import json
import os

from twisted import web
from torweb.api.ressources import TorInstances

__all__ = ('TorwebResource', 'ApiResource')


class TorwebResource(web.resource.Resource):
    '''
    The root resource for all resources provided by the webserver.
    These are the following:

      * `app`: The webpage for the user interface
      * `api`: The RESTful API (:class:`ApiRessource`).
    '''

    def __init__(self, basedir):
        web.resource.Resource.__init__(self)

        with open(os.path.join(basedir, 'torweb.json'), 'r') as config:
            connections = json.load(config)

        self.putChild('', web.util.Redirect('/app'))
        self.putChild('app', web.static.File(
            os.path.abspath(os.path.join(basedir, 'app'))))
        self.putChild('api', ApiResource(connections))


class ApiResource(web.resource.Resource):
    '''
    RESTful API definition. Currently contains
    only one child:

      * `../tor`: :class:`api.torinstance.TorInstances`.
    '''

    def __init__(self, config):
        web.resource.Resource.__init__(self)
        self.putChild('tor', TorInstances(config))
