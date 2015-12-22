# -*- coding: utf-8 -*-

from twisted.trial import unittest

from torweb.api.ressources import base
from .util import DummyTorState, render
from twisted.web.test.test_web import DummyRequest
import json


class MyTorResource(base.TorResource):
    json_list_class = 1
    json_detail_class = 1


class JsonClass(object):

    def __init__(self, obj):
        self.object = obj

    def as_dict(self):
        return {'object': self.object}


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

    def test_get_list_notimplemented(self):
        class MyTorResource(base.TorResource):
            json_list_class = 1
            json_detail_class = 1
        r = MyTorResource()
        try:
            r.get_list()
            self.fail("Nothing thrown")
        except NotImplementedError:
            pass

        try:
            r.get_by_id(0)
            self.fail("Nothing thrown")
        except NotImplementedError:
            pass

    def test_default_detail_class(self):
        class MyTorResource(base.TorResource):
            json_list_class = 1
            json_detail_class = 1

            def get_by_id(self, ident):
                return ident

        request = DummyRequest([''])
        r = MyTorResource(self.torstate)
        child = r.getChildWithDefault('1', request)
        self.assertIsInstance(child, base.TorResourceDetail)

    def test_custom_detail_class(self):
        class A(base.TorResourceDetail):

            def render_POST(self, request):
                self.post_rendered = True
                return "worked"

        class MyTorResource(base.TorResource):
            json_list_class = 1
            json_detail_class = 1
            detail_class = A

            def get_by_id(self, ident):
                return ident

        request = DummyRequest([''])
        r = MyTorResource(self.torstate)
        child = r.getChildWithDefault('1', request)
        self.assertIsInstance(child, A)

    def test_render_list(self):
        class A(object):

            def render_POST(self, request):
                self.post_rendered = True
                return "worked"

        class MyTorResource(base.TorResource):
            json_list_class = JsonClass
            json_detail_class = JsonClass
            detail_class = A

            def get_list(self):
                return range(100)

        request = DummyRequest([''])
        request.responseCode = 200
        resource = MyTorResource(self.torstate)
        d = render(resource, request)

        def onresponse(_):
            self.assertEquals(request.responseCode, 200)
            payload = ''.join(request.written)
            payload = json.loads(payload.decode('utf-8'))
            self.assertIsInstance(payload, dict)
            self.assertTrue('objects' in payload)
            self.assertTrue(len(payload['objects']) == 100)
            for i, item in enumerate(payload['objects']):
                self.assertTrue('object' in item)
                self.assertEquals(item['object'], i)

        d.addCallback(onresponse)
        d.addErrback(self.fail)
