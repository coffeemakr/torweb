# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

from twisted.web import server, resource, http, static, util
from twisted.internet import reactor
from torweb.api.ressources import DNSRoot, TorInstances

import txtorcon
import os
import json


class RootResource(resource.Resource):
    def __init__(self, basedir):
        resource.Resource.__init__(self)

        with open(os.path.join(basedir, 'connections.json'), 'r') as config:
            connections = json.load(config)

        self.putChild('', util.Redirect('/app'))
        self.putChild('app', static.File(os.path.abspath(os.path.join(basedir, 'app'))))
        self.putChild('api', ApiRessource(connections))


class ApiRessource(resource.Resource):
    '''
    RESTful API definition.
    '''
    def __init__(self, config):
        resource.Resource.__init__(self)
        self.putChild('dns', DNSRoot())
        self.putChild('tor', TorInstances(config))

    
def main():
    from twisted.python import log
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tls", action="store_true", default=False)
    args = parser.parse_args()
    log.startLogging(sys.stdout)
    #messageStore = message.MessageStore(sys.argv[1])
    rootFolder = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
    s = server.Site(RootResource(rootFolder))
    if args.tls:
        from twisted.internet import ssl
        with open(os.path.join(rootFolder, 'key.pem')) as certFile:
            certData = certFile.read()
        with open(os.path.join(rootFolder, 'cert.pem')) as certFile:
            certData += certFile.read()

        certificate = ssl.PrivateCertificate.loadPEM(certData)
        reactor.listenSSL(8083, s, certificate.options(), interface='127.0.0.1')
    else:
        reactor.listenTCP(8082, s, interface='127.0.0.1')
    reactor.run()

if __name__ == "__main__":
    main()