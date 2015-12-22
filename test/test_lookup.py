# -*- coding: utf-8 -*-

from twisted.trial import unittest

from torweb.api.ressources import lookup
from twisted.web.test.test_web import DummyRequest
from .util import render

import json

class TestLookup(unittest.TestCase):
	def test_get_reverse_dns(self):
		request = DummyRequest([])
		root = lookup.DNSRoot()
		reverse_root = root.getChildWithDefault('reverse', request)
		self.assertIsInstance(reverse_root, lookup.ReverseDNSRoot)
		reverse = reverse_root.getChildWithDefault('localhost', reverse_root)
		self.assertIsInstance(reverse, lookup.ReverseDNS)

	def test_reverse_dns_google(self):
		reverse = lookup.ReverseDNS('8.8.8.8')
		request = DummyRequest([])
		d = render(reverse, request)
		def rendered(_):
			payload = ''.join(request.written)
			payload = json.loads(payload.decode('utf-8'))
			self.assertIsInstance(payload, dict)
			self.assertTrue('ips' in payload)
			self.assertTrue('host' in payload)
			self.assertTrue('alias' in payload)
			self.assertEquals(payload['host'], 'google-public-dns-a.google.com')
			self.assertTrue('8.8.8.8' in payload['ips'])
		d.addCallback(rendered)
