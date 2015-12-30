# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

from twisted.web import resource
from torweb.api.util import response
from twisted.web import server
from twisted.names import dns
import json

__all__ = ('DNSRoot', 'ReverseDNS')


class DNSConfig(object):
    resolver = None


class DNSResource(resource.Resource):

    def __init__(self, resolver=None, config=None):
        resource.Resource.__init__(self)
        if config is None:
            config = DNSConfig()
        if resolver is not None:
            config.resolver = resolver
        self.config = config


class DNSRoot(DNSResource):

    def __init__(self, *args, **kwargs):
        DNSResource.__init__(self, *args, **kwargs)
        self.putChild('reverse', ReverseDNS(config=self.config))
        self.putChild('A', DNSTypeLookup(type=dns.A, config=self.config))
        self.putChild('AAAA', DNSTypeLookup(type=dns.AAAA, config=self.config))


class DNSTypeLookup(DNSResource):

    type = dns.A

    cls = dns.IN

    def __init__(self, type=None, cls=None, **kwargs):
        DNSResource.__init__(self, **kwargs)
        if type is not None:
            self.type = type

        if cls is not None:
            self.cls = cls

    def get_query(self, name):
        return dns.Query(name, type=self.type, cls=self.cls)

    def getChild(self, name, request):
        query = self.get_query(name)
        return DNSLookup(query, config=self.config)


class ReverseDNS(DNSTypeLookup):

    type = dns.PTR

    def getChild(self, ip, request):
        '''
        Converts the ip address to a resolvable address.
        '''
        ip = ip.split('.')
        ip.reverse()
        ip = '.'.join(ip) + '.in-addr.arpa'
        query = self.get_query(ip)
        return DNSLookup(query, config=self.config)


class DNSLookup(DNSResource):

    timeout = (5,)

    def __init__(self, query, **kwargs):
        DNSResource.__init__(self, **kwargs)
        self.query = query

    def call(self, timeout=None):
        return self.config.resolver.query(self.query, timeout=self.timeout)

    def _serialize_answers(self, answers):
        result = []
        if answers:
            attribute = None
            if hasattr(answers[0], 'payload'):
                for i, answer in enumerate(answers):
                    answers[i] = answer.payload
            for attr in ('name', 'address'):
                if hasattr(answers[0], attr):
                    attribute = attr
            if attribute is None:
                try:
                    typename = type(answers[0]).__name__
                except AttributeError:
                    typename = str(type(answers[0]))
                raise RuntimeError("DNS answer not understood (%s)" % typename)
            for answer in answers:
                serialized = {'ttl': answer.ttl}
                value = str(getattr(answer, attribute))
                if attribute == 'address':
                    ip = ""
                    for b in value:
                        ip += str(ord(b)) + '.'
                    value = ip[:-1]
                serialized[attribute] = value
                result.append(serialized)
        return result

    def _render_callback(self, data, request):
        answers, auth, add = data
        result = {'objects': self._serialize_answers(answers)}
        response.send_json(request, result)

    def _render_error(self, error, request):
        error.printTraceback()
        result = response.error_tb(error)
        response.send_json(request, result)

    @response.json
    def render_GET(self, request):
        d = self.call()
        d.addCallback(self._render_callback, request)
        d.addErrback(self._render_error, request)
        return server.NOT_DONE_YET
