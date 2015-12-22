# -*- coding: utf-8 -*-

from twisted.trial import unittest

from torweb.api.ressources import base
from .util import DummyTorState

class MyTorResource(base.TorResource):
    json_list_class = 1
    json_detail_class = 1

class TestTorResourceBase(unittest.TestCase):

    def setUp(self):
        self.torstate = DummyTorState()

    def test_set_torstate_afterwards(self):
        r = MyTorResource()
        self.assertEquals(r.torstate, None)
        self.assertEquals(r.get_torstate(), None)
        r.set_torstate(self.torstate)
        self.assertEquals(r.torstate, self.torstate)
        self.assertEquals(r.get_torstate(), self.torstate)

    def test_set_torstate_in_constructor(self):
        r = MyTorResource(self.torstate)
        self.assertEquals(r.torstate, self.torstate)
        self.assertEquals(r.get_torstate(), self.torstate)

    def test_json_list_class_not_set(self):
        class MyTorResource1(base.TorResource):
            json_list_class = None
            json_detail_class = 1

        class MyTorResource2(base.TorResource):
            json_list_class = 1
            json_detail_class = None

        try:
            MyTorResource1()
            self.fail("No exception thrown for MyTorResource1")
        except RuntimeError as why:
            self.assertTrue('json_list_class' in str(why))

        try:
            MyTorResource2()
            self.fail("No exception thrown for MyTorResource2")
        except RuntimeError as why:
            self.assertTrue('json_detail_class' in str(why))