import txtorcon
from txtorcon.torcontrolprotocol import parse_keywords
from txtorcon.log import txtorlog
from twisted.internet.interfaces import IProtocolFactory
from zope.interface import implementer
from twisted.internet import reactor, defer
import os
import base64
import re


class TorControlProtocol(txtorcon.TorControlProtocol):
    '''
    Forked by copypasta and customized txtorcon.TorControlProtocol.

    Functional changes:
        
        * If cookie authentication failes due an IOError,
          password authentication is used.
    '''
    
    def _do_safecookie_auth(self, protoinfo):
        cookie = re.search('COOKIEFILE="(.*)"', protoinfo).group(1)
        self.cookie_data = open(cookie, 'r').read()
        if len(self.cookie_data) != 32:
            raise RuntimeError(
                "Expected authentication cookie to be 32 bytes, got %d" %
                len(self.cookie_data)
            )
        txtorlog.msg("Using SAFECOOKIE authentication", cookie,
                     len(self.cookie_data), "bytes")
        self.client_nonce = os.urandom(32)

        cmd = 'AUTHCHALLENGE SAFECOOKIE ' + \
              base64.b16encode(self.client_nonce)
        d = self.queue_command(cmd)
        d.addCallback(self._safecookie_authchallenge)
        d.addCallback(self._bootstrap)
        d.addErrback(self._auth_failed)
        return

    def _do_cookie_auth(self, protoinfo):
        cookie = re.search('COOKIEFILE="(.*)"', protoinfo).group(1)
        with open(cookie, 'r') as cookiefile:
            data = cookiefile.read()
        if len(data) != 32:
            raise RuntimeError(
                "Expected authentication cookie to be 32 "
                "bytes, got %d instead." % len(data)
            )
        txtorlog.msg("Using COOKIE authentication",
                     cookie, len(data), "bytes")
        d = self.authenticate(data)
        d.addCallback(self._bootstrap)
        d.addErrback(self._auth_failed)

    def _do_authenticate(self, protoinfo):
        """
        Callback on PROTOCOLINFO to actually authenticate once we know
        what's supported.
        """

        methods = None
        for line in protoinfo.split('\n'):
            if line[:5] == 'AUTH ':
                kw = parse_keywords(line[5:].replace(' ', '\n'))
                methods = kw['METHODS'].split(',')
        if not methods:
            raise RuntimeError(
                "Didn't find AUTH line in PROTOCOLINFO response."
            )

        if 'SAFECOOKIE' in methods:
            try:
                return self._do_safecookie_auth(protoinfo)
            except IOError as why:
                print("Failed to read SAFECOOKIE:"  + str(why))
                pass

        if 'COOKIE' in methods:
            try:
                return self._do_cookie_auth(protoinfo)
            except IOError:
                print("Failed to read COOKIE:"  + str(why))
                pass

        if self.password_function:
            d = defer.maybeDeferred(self.password_function)
            d.addCallback(self._do_password_authentication)
            d.addErrback(self._auth_failed)
            return

        raise RuntimeError(
            "The Tor I connected to doesn't support SAFECOOKIE nor COOKIE"
            " authentication and I have no password_function specified"
            " or authentication with HASHEDPASSWORD is not allowed."
        )


class TorProtocolFactory(txtorcon.TorProtocolFactory):
    '''
    Factory for costumized :class:`TorControlProtocol'
    '''
    protocol = TorControlProtocol

    def buildProtocol(self, addr):
        ":api:`twisted.internet.interfaces.IProtocolFactory` API"
        proto = self.protocol(self.password_function)
        proto.factory = self
        return proto