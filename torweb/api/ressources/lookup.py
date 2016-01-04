# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

from twisted.web import resource
from torweb.api.util import response
from twisted.web import server
from twisted.names import dns
import json

__all__ = ('DNSRoot', 'ReverseDNS')


class DNSConfig(object):
    '''
    Configuration for all :class:`DNSResource`
    '''
    resolver = None


class DNSResource(resource.Resource):
    '''
    Base class for all DNS related resources.
    '''

    def __init__(self, resolver=None, config=None):
        resource.Resource.__init__(self)
        if config is None:
            config = DNSConfig()
        elif not isinstance(config, DNSConfig):
            raise TypeError("expected DNSConfig")
        if resolver is not None:
            config.resolver = resolver
        self.config = config


class DNSRoot(DNSResource):
    '''
    DNS API root resource.
    '''

    def __init__(self, *args, **kwargs):
        DNSResource.__init__(self, *args, **kwargs)
        self.putChild('reverse', ReverseDNS(config=self.config))
        self.putChild('A', DNSTypeLookup(type_=dns.A, config=self.config))
        self.putChild('AAAA', DNSTypeLookup(
            type_=dns.AAAA, config=self.config))


class DNSTypeLookup(DNSResource):
    '''
    Resource which creates a :class:`twisted.names.dns.Query` object for
    every :meth:`getChild` call.
    '''

    #: The DNS type. See :attr:`twisted.names.dns.Query.type`.
    type = dns.A

    #: The DNS class. See :attr:`twisted.names.dns.Query.cls`.
    cls = dns.IN

    def __init__(self, type_=None, cls=None, **kwargs):
        '''
        Create a new DNSTypeLookup resource.
        :param type_: The DNS lookup type (e.g. `A` or `AAAA`).
        :param cls: The DNS lookup class. Defaults to :const:`dns.IN`
        '''
        DNSResource.__init__(self, **kwargs)
        if type_ is not None:
            self.type = type_

        if cls is not None:
            self.cls = cls

    def _get_query(self, name):
        '''
        Returns a :class:`twisted.names.dns.Query` object.
        '''
        return dns.Query(name, type=self.type, cls=self.cls)

    def getChild(self, name, request):
        query = self._get_query(name)
        return DNSLookup(query, config=self.config)


class ReverseDNS(DNSTypeLookup):
    '''
    Resource to lookup any IP-address.
    '''

    #: The lookup type is PTR (Pointer)
    type = dns.PTR

    def getChild(self, ip, request):
        '''
        Returns a :class:`DNSLookup` object for a requested  IP-Address.
        The IP-Address is converted to perform a reverse lookup. For example
        if the path /1.2.3.4 is requested a PTR DNS lookup for
        `4.3.2.1.in-addr.arpa` is returned.
        '''
        ip = ip.split('.')
        ip.reverse()
        ip = '.'.join(ip) + '.in-addr.arpa'
        query = self._get_query(ip)
        return DNSLookup(query, config=self.config)


class DNSLookup(DNSResource):
    '''
    Resource which calls a DNS query when it it rendered.
    '''

    #: The time-out in seconds.
    timeout = (5,)

    def __init__(self, query, **kwargs):
        '''
        :param query: :class:`twisted.names.dns.Query` object.
        '''
        DNSResource.__init__(self, **kwargs)
        self.query = query

    def call(self, timeout=None):
        '''
        Calls the query.
        Returns a deferred.
        '''
        return self.config.resolver.query(self.query, timeout=self.timeout)

    def _serialize_answers(self, answers):
        '''
        Tries to serialize all answers to dictionaries.
        '''
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
                # try get the type name of the answer for the error message
                try:
                    typename = type(answers[0]).__name__
                except AttributeError:
                    typename = str(type(answers[0]))
                raise RuntimeError("DNS answer not understood (%s)" % typename)
            for answer in answers:
                serialized = {'ttl': answer.ttl}
                value = str(getattr(answer, attribute))
                if attribute == 'address':
                    ip_addr = ""
                    for byte_ in value:
                        ip_addr += str(ord(byte_)) + '.'
                    value = ip_addr[:-1]
                serialized[attribute] = value
                result.append(serialized)
        return result

    def _render_callback(self, data, request):
        '''
        Callback when the DNS answer arrives. This creates a
        JSON objects with all answers in "objects"::

            {
                "objects": [ <answers> ]
            }

        This method calls :meth:`_serialize_answers`.
        '''
        answers, _, _ = data
        result = {'objects': self._serialize_answers(answers)}
        response.send_json(request, result)

    def _render_error(self, error, request):
        '''
        Callback when the DNS lookup fails.
        '''
        error.printTraceback()
        result = response.error_tb(error)
        response.send_json(request, result)

    @response.encode
    def render_GET(self, request):
        '''
        Renders a GET request.
        '''
        deferred = self.call()
        deferred.addCallback(self._render_callback, request)
        deferred.addErrback(self._render_error, request)
        return server.NOT_DONE_YET
