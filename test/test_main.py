# -*- coding: utf-8 -*-

from twisted.trial import unittest

class TestMain(unittest.TestCase):
    def test_main_exists(self):
        from torweb import __main__
        self.assertTrue(hasattr(__main__, 'main'))
