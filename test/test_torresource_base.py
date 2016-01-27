# -*- coding: utf-8 -*-

from twisted.trial import unittest

from torweb.api.ressources import base, instanceconfig
from .util import DummyTorState, render
from twisted.web.test.test_web import DummyRequest
from torweb.api.util.response import NoResource
from twisted.internet.defer import inlineCallbacks
import json
from torweb.api.json import base as jsonbase
from torweb.api.util import response
import zope.interface


class JsonClass(object):
    zope.interface.implements(jsonbase.IJSONSerializable)

    def __init__(self, obj):
        self.object = obj

    def as_dict(self):
        'Returns a dict'
        return {'object': self.object}


class TorResourceWithJson(base.TorResource):
    "Test resource"

    zope.interface.implements(base.ITorResource)

    json_list_class = JsonClass
    json_detail_class = JsonClass

    def get_by_id(self, ident):
        return {"object": ident}

    def get_list(self):
        return [1, 2, 3]


class TestTorResourceBase(unittest.TestCase):

    def setUp(self):
        self.torstate = DummyTorState()
        self.instanceconfig = instanceconfig.TorInstanceConfig()
        self.instanceconfig.state = self.torstate
        self.request = DummyRequest([''])
        self.request.requestHeaders.addRawHeader(
            'accept', 'application/json;charset=utf-8')

    def test_default_detail_class(self):
        class TorResourceWithJson1(TorResourceWithJson):

            def get_by_id(self, ident):
                return ident

        r = TorResourceWithJson1(self.instanceconfig)
        child = r.getChildWithDefault('1', self.request)
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

        r = TorResourceWithJson1(self.instanceconfig)
        child = r.getChildWithDefault('1', self.request)
        self.assertIsInstance(child, A)

    def test_invalid_identifier(self):
        class LocalTorResource(TorResourceWithJson):

            def get_by_id(self, ident):
                raise ValueError

        r = LocalTorResource(self.instanceconfig)
        child = r.getChildWithDefault('1', self.request)
        self.assertIsInstance(child, NoResource)

    def test_empty_identifier(self):
        parent = self

        class LocalTorResource(TorResourceWithJson):

            def get_by_id(self, ident):
                parent.fail("get_by_id called")

        r = LocalTorResource(self.instanceconfig)
        child = r.getChildWithDefault('', self.request)
        self.assertIsInstance(child, NoResource)

    def test_unexisting_identifier(self):

        class LocalTorResource(TorResourceWithJson):

            def get_by_id(self, ident):
                return None

        r = LocalTorResource(self.instanceconfig)
        child = r.getChildWithDefault('1', self.request)
        self.assertIsInstance(child, NoResource)

    @inlineCallbacks
    def test_render_list(self):
        class LocalTorResource(TorResourceWithJson):

            def get_list(self):
                return range(100)

        self.request.responseCode = 200
        resource = LocalTorResource(self.instanceconfig)
        d = yield render(resource, self.request)

        self.assertEquals(self.request.responseCode, 200,
                          msg=self.request.responseCode)
        payload = ''.join(self.request.written)
        payload = json.loads(payload.decode('utf-8'))
        self.assertIsInstance(payload, dict)
        self.assertTrue('objects' in payload, msg="Didn't receive objects: {}".format(payload))
        self.assertTrue(len(payload['objects']) == 100)
        for i, item in enumerate(payload['objects']):
            self.assertTrue('object' in item)
            self.assertEquals(item['object'], i)

    @inlineCallbacks
    def test_render_list_without_state(self):

        class LocalTorResource(TorResourceWithJson):

            def get_list(self):
                return range(100)

        self.request.responseCode = 200
        resource = LocalTorResource()
        d = yield render(resource, self.request)

        self.assertEquals(self.request.responseCode, 200,
                          msg=self.request.responseCode)
        payload = ''.join(self.request.written)
        payload = json.loads(payload.decode('utf-8'))
        self.assertIsInstance(payload, dict)
        self.assertTrue('error' in payload, msg=payload)

    def test_get_child_without_state(self):
        class LocalTorResource(TorResourceWithJson):

            def get_by_id(self, ident):
                raise RuntimeError("called")

        self.request.responseCode = 200
        resource = LocalTorResource()
        child = resource.getChildWithDefault('1', self.request)
        self.assertIsInstance(child, response.JsonError)


class TestTorResourceDetail(unittest.TestCase):
    def setUp(self):
        self.request = DummyRequest([''])
        self.request.requestHeaders.addRawHeader(
            'accept', 'application/json;charset=utf-8')

    def test_render(self):
        r = base.TorResourceDetail(1, JsonClass)
        d = render(r, self.request)

        def checkResult(*args):
            payload = ''.join(self.request.written)
            payload = json.loads(payload.decode('utf-8'))
            self.assertIsInstance(payload, dict)
            self.assertEqual(payload['object'], 1)

        d.addCallback(checkResult)
        d.addErrback(self.fail)
