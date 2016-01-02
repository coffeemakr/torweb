# -*- coding: utf-8 -*-

from twisted.trial import unittest

from torweb.api.ressources import lookup
from twisted.internet import defer
from twisted.web.test.test_web import DummyRequest
from twisted.internet.base import DelayedCall
from twisted.names import client

from .util import render
import json

DelayedCall.debug = True


class TestReverseLookup(unittest.TestCase):

    def setUp(self):
        self.config = lookup.DNSConfig()
        resolver = client.Resolver(servers=[('8.8.8.8', 53)])
        self.config.resolver = resolver

    @defer.inlineCallbacks
    def test_get_reverse_dns(self):
        request = DummyRequest([])
        root = lookup.DNSRoot(config=self.config)
        reverse_root = yield root.getChildWithDefault('reverse', request)
        self.assertIsInstance(reverse_root, lookup.ReverseDNS)
        reverse = yield reverse_root.getChildWithDefault('localhost', reverse_root)
        self.assertIsInstance(reverse, lookup.DNSLookup)

    @defer.inlineCallbacks
    def test_reverse_dns_google(self):
        request = DummyRequest([])
        reverse = yield lookup.ReverseDNS(config=self.config).getChildWithDefault('8.8.8.8', request)
        result = yield render(reverse, request)
        payload = ''.join(request.written)
        payload = json.loads(payload.decode('utf-8'))
        self.assertIsInstance(payload, dict)
        self.assertTrue('objects' in payload)
        for obj in payload['objects']:
            self.assertEquals(
                obj['name'], 'google-public-dns-a.google.com')

    @defer.inlineCallbacks
    def test_reverse_dns_unexisting_dns(self):
        request = DummyRequest([])
        reverse = lookup.ReverseDNS(
            config=self.config).getChildWithDefault('1.1.1.1', request)
        d = yield render(reverse, request)

        payload = ''.join(request.written)
        payload = json.loads(payload.decode('utf-8'))
        self.assertIsInstance(payload, dict)
        self.assertTrue('error' in payload)
        self.assertTrue(type(payload['error']) == dict)
    
