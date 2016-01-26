#!/usr/bin/env python
# coding=utf-8
'''
The server module contains the essential resources to start the webserver
from console on via python calls.

Starting from Commandline
-------------------------

The server can be started by e xecuting the module directly::

   python -m torweb

This will call :func:`main()`. You can call ``python -m torweb --help`` to
see all available options.
'''

from __future__ import absolute_import, print_function, with_statement

import argparse
import os
import sys

from twisted import python
from twisted.internet import reactor
from twisted.web import server

from torweb import configuration as config
from torweb import data

from .torweb import TorwebResource


class TorwebConfiguration(config.Configuration):

    _name_connections = 'connections'
    _name_includes = 'include configuration'

    root_entry = config.DictEntry({
        _name_connections: config.ListEntry(config.DictEntry({
            'name': config.StringEntry(),
            'host': config.StringEntry(),
            'port': config.IntegerEntry(),
            'password': config.StringEntry()
        })),
        _name_includes: config.ListEntry(config.StringEntry())
    })

    @property
    def include_configuration_files(self):
        return self.value[self._name_includes]


def get_configuration(filename=None):
    if filename is None:
        filename = data.default_configuration()
    config = TorwebConfiguration(configfile=filename)

    # TODO: implement configuration file includes

    '''
    files = config.include_configuration_files

    for filename in files:
        if os.path.isfile(filename):
            config.read_file(filename)
    '''
    return config


def main():
    '''
    Run the torweb server from command line arguments.
    '''
    parser = argparse.ArgumentParser(prog="torweb")
    parser.add_argument("port", nargs='?', metavar="PORT", default=8082,
                        type=int, help="Port to listen on. Default: 8082")
    parser.add_argument("--listen-address", metavar="IP",
                        help=("USE CAREFULLY! Set the IP-Address "
                              "on which torweb listens."),
                        default='127.0.0.1')
    parser.add_argument("-t", "--tls", action="store_true",
                        help="Use TLS encryption.")
    parser.add_argument("-c", "--config", default="None",
                        help="Set the configuration file.")
    parser.add_argument("-k", "--private-key", default=None,
                        help=("Path to the private key in PEM "
                              "format for TLS encryption."))
    parser.add_argument("-C", "--certificate", default=None,
                        help=("Path to the public certificate in PEM "
                              "format for TLS encryption."))
    parser.add_argument(
        "-q", "--quiet", help="Don't log messages.", action="store_true")

    args = parser.parse_args()

    if not args.quiet:
        python.log.startLogging(sys.stdout)

    root_folder = data.get_path()

    if args.private_key is None:
        args.private_key = os.path.join(root_folder, 'key.pem')

    if args.certificate is None:
        args.certificate = os.path.join(root_folder, 'cert.pem')

    torweb_resource = TorwebResource()
    site = server.Site(torweb_resource)

    if args.tls:
        try:
            from twisted.internet import ssl
        except ImportError as why:
            parser.error("Failed to import ssl: " + str(why))

        if not os.path.isfile(args.private_key):
            parser.error("Key file {} doesn't exist".format(args.private_key))

        if not os.path.isfile(args.certificate):
            parser.error(
                "Certificate file {} doesn't exist".format(args.certificate))

        cert_data = ""
        with open(args.private_key) as cert_file:
            cert_data = cert_file.read()

        with open(args.certificate) as cert_file:
            cert_data += cert_file.read()

        certificate = ssl.PrivateCertificate.loadPEM(cert_data)
        reactor.listenSSL(args.port, site, certificate.options(),
                          interface=args.listen_address)
    else:
        reactor.listenTCP(args.port, site, interface=args.listen_address)
    reactor.run()

if __name__ == "__main__":
    main()
