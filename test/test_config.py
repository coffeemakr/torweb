# -*- coding: utf-8 -*-

from twisted.trial import unittest

from torweb.api.ressources import circuit
from .util import TorProcess
class TestConfig(unittest.TestCase):
	def setUp(self):
		self.tor = TorProcess()

	def tearDown(self):
		self.tor.end()
