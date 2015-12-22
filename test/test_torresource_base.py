# -*- coding: utf-8 -*-

from twisted.trial import unittest

from torweb.api.ressources import base
from .util import DummyTorState, render
from twisted.web.test.test_web import DummyRequest
from twisted.web.resource import NoResource
import json

class JsonClass(object):

    def __init__(self, obj):
        self.object = obj

    def as_dict(self):
        return {'object': self.object}

class TorResourceWithJson(base.TorResource):
    json_list_class = JsonClass
    json_detail_class = JsonClass




class TestTorResourceBase(unittest.TestCase):

    def setUp(self):
        self.torstate = DummyTorState()

    def test_set_torstate_afterwards(self):
        r = TorResourceWithJson()
        self.assertEquals(r.torstate, None)
        self.assertEquals(r.get_torstate(), None)
        r.set_torstate(self.torstate)
        self.assertEquals(r.torstate, self.torstate)
        self.assertEquals(r.get_torstate(), self.torstate)

    def test_set_torstate_in_constructor(self):
        r = TorResourceWithJson(self.torstate)
        self.assertEquals(r.torstate, self.torstate)
        self.assertEquals(r.get_torstate(), self.torstate)

    def test_json_list_class_not_set(self):
        class TorResourceWithJson1(base.TorResource):
            json_list_class = None
            json_detail_class = JsonClass

        class TorResourceWithJson2(base.TorResource):
            json_detail_class = None
            json_list_class = JsonClass

        try:
            TorResourceWithJson1()
            self.fail("No exception thrown for TorResourceWithJson1")
        except RuntimeError as why:
            self.assertTrue('json_list_class' in str(why))

        try:
            TorResourceWithJson2()
            self.fail("No exception thrown for TorResourceWithJson2")
        except RuntimeError as why:
            self.assertTrue('json_detail_class' in str(why))

    def test_get_list_notimplemented(self):

        r = TorResourceWithJson()
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
        class TorResourceWithJson1(TorResourceWithJson):

            def get_by_id(self, ident):
                return ident

        request = DummyRequest([''])
        r = TorResourceWithJson1(self.torstate)
        child = r.getChildWithDefault('1', request)
        self.assertIsInstance(child, base.TorResourceDetail)

    def test_custom_detail_class(self):
        class A(base.TorResourceDetail):

            def render_POST(self, request):
                self.post_rendered = True
                return "worked"

        class TorResourceWithJson1(TorResourceWithJson):
            detail_class = A

            def get_by_id(self, ident):
                return ident

        request = DummyRequest([''])
        r = TorResourceWithJson1(self.torstate)
        child = r.getChildWithDefault('1', request)
        self.assertIsInstance(child, A)

    def test_invalid_identifier(self):
        class LocalTorResource(TorResourceWithJson):

            def get_by_id(self, ident):
                raise ValueError

        request = DummyRequest([''])
        r = LocalTorResource(self.torstate)
        child = r.getChildWithDefault('1', request)
        self.assertIsInstance(child, NoResource)

    def test_empty_identifier(self):
        parent = self
        class LocalTorResource(TorResourceWithJson):
            def get_by_id(self, ident):
                parent.fail("get_by_id called")

        request = DummyRequest([''])
        r = LocalTorResource(self.torstate)
        child = r.getChildWithDefault('', request)
        self.assertIsInstance(child, NoResource)

    def test_unexisting_identifier(self):

        class LocalTorResource(TorResourceWithJson):

            def get_by_id(self, ident):
                return None

        request = DummyRequest([''])
        r = LocalTorResource(self.torstate)
        child = r.getChildWithDefault('1', request)
        self.assertIsInstance(child, NoResource)

    def test_render_list(self):
        class LocalTorResource(TorResourceWithJson):

            def get_list(self):
                return range(100)

        request = DummyRequest([''])
        request.responseCode = 200
        resource = LocalTorResource(self.torstate)
        d = render(resource, request)

        def onresponse(_):
            self.assertEquals(request.responseCode, 200,
                              msg=request.responseCode)
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

    def test_render_list_without_state(self):

        class LocalTorResource(TorResourceWithJson):

            def get_list(self):
                return range(100)

        request = DummyRequest([''])
        request.responseCode = 200
        resource = LocalTorResource()
        d = render(resource, request)

        def onresponse(_):
            self.assertEquals(request.responseCode, 200,
                              msg=request.responseCode)
            payload = ''.join(request.written)
            payload = json.loads(payload.decode('utf-8'))
            self.assertIsInstance(payload, dict)
            self.assertTrue('error' in payload, msg=payload)
            self.assertTrue('state' in payload['error'], msg=payload['error'])
        d.addCallback(onresponse)
        d.addErrback(self.fail)

    def test_get_child_without_satte(self):
        class LocalTorResource(TorResourceWithJson):
            def get_by_id(self, ident):
                raise RuntimeError("called")

        request = DummyRequest([''])
        request.responseCode = 200
        resource = LocalTorResource()
        child = resource.getChildWithDefault('1', request)
        self.assertIsInstance(child, NoResource)

class TestTorResourceDetail(unittest.TestCase):
    def test_render(self):
        r = base.TorResourceDetail(1, JsonClass)
        request = DummyRequest([])
        d = render(r, request)

        def checkResult(*args):
            payload = ''.join(request.written)
            payload = json.loads(payload.decode('utf-8'))
            self.assertIsInstance(payload, dict)
            self.assertEqual(payload['object'], 1)

        d.addCallback(checkResult)
        d.addErrback(self.fail)