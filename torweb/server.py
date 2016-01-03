# -*- coding: utf-8 -*-
'''
The server module contains the essential resources to start the webserver
from console on via python calls.

Starting from Commandline
-------------------------

The server can be started by executing the module directly::

   python -m torweb

You can call `python -m torweb --help` to see all available options.

'''

from __future__ import absolute_import, print_function, with_statement

from twisted.web import server, resource, static, util
from twisted.internet import reactor
from torweb.api.ressources import TorInstances

import os
import json


class RootResource(resource.Resource):
    '''
    The root resource for all resources provided by the webserver.
    These are the following:

      * `/app`: The webpage for the user interface
      * `/api`: The RESTful API.
    '''

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
    RESTful API definition. Currently contains
    only one child:

      * `../tor`: :class:`api.torinstance.TorInstances`.
    '''

    def __init__(self, config):
        resource.Resource.__init__(self)
        self.putChild('tor', TorInstances(config))


def main():
    '''
    Run the torweb server from command line arguments.
    '''
    from twisted.python import log
    import sys
    import argparse
    parser = argparse.ArgumentParser(prog="torweb")
    parser.add_argument("port", nargs='?', metavar="PORT", default=8082,
                        type=int, help="Port to listen on. Default: 8082")
    parser.add_argument("--listen-address", metavar="IP",
                        help=("USE CAREFULLY! Set the IP-Address "
                              "on which torweb listens."),
                        default='127.0.0.1')
    parser.add_argument("-t", "--tls", action="store_true",
                        help="Use TLS encryption.")
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

    root_folder = os.path.abspath(
        os.path.join(os.path.split(__file__)[0], '..'))
    site = server.Site(RootResource(root_folder))
    if args.tls:
        from twisted.internet import ssl
        cert_data = ""
        with open(os.path.join(root_folder, args.private_key)) as cert_file:
            cert_data = cert_file.read()
        with open(os.path.join(root_folder, args.certificate)) as cert_file:
            cert_data += cert_file.read()

        certificate = ssl.PrivateCertificate.loadPEM(cert_data)
        reactor.listenSSL(args.port, site, certificate.options(),
                          interface=args.listen_address)
    else:
        reactor.listenTCP(args.port, site, interface=args.listen_address)
    reactor.run()

if __name__ == "__main__":
    main()
