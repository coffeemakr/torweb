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

        with open(os.path.join(basedir, 'torweb.json'), 'r') as config:
            connections = json.load(config)

        self.putChild('', util.Redirect('/app'))
        self.putChild('app', static.File(
            os.path.abspath(os.path.join(basedir, 'app'))))
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
    parser = argparse.ArgumentParser(prog="torweb")
    parser.add_argument("port", nargs='?', metavar="PORT", default=8082,
                        type=int, help="Port to listen on. Default: 8082")
    parser.add_argument("--listen-address", metavar="IP",
                        help=("USE CAREFULLY! Set the IP-Address "
                              "on which torweb listens."))
    parser.add_argument("-t", "--tls", action="store_true",
                        default=False, help="Use TLS encryption.")
    parser.add_argument("-c", "--config", default="connections.json",
                        help="Set the configuration file.")
    parser.add_argument("-k", "--private-key", default="key.pem",
                        help=("Path to the private key in PEM "
                              "format for TLS encryption."))
    parser.add_argument("-C", "--certificate", default="cert.pem",
                        help=("Path to the public certificate in PEM "
                              "format for TLS encryption."))
    parser.add_argument(
        "-q", "--quiet", help="Don't log messages.", action="store_true")

    args = parser.parse_args()

    if not args.quiet:
        log.startLogging(sys.stdout)

    rootFolder = os.path.abspath(
        os.path.join(os.path.split(__file__)[0], '..'))
    s = server.Site(RootResource(rootFolder))
    if args.tls:
        from twisted.internet import ssl
        with open(os.path.join(rootFolder, 'key.pem')) as certFile:
            certData = certFile.read()
        with open(os.path.join(rootFolder, 'cert.pem')) as certFile:
            certData += certFile.read()

        certificate = ssl.PrivateCertificate.loadPEM(certData)
        reactor.listenSSL(args.port, s, certificate.options(),
                          interface='127.0.0.1')
    else:
        reactor.listenTCP(args.port, s, interface='127.0.0.1')
    reactor.run()

if __name__ == "__main__":
    main()
