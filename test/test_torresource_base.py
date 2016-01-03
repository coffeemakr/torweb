# -*- coding: utf-8 -*-

from twisted.trial import unittest

from torweb.api.ressources import base, instanceconfig
from .util import DummyTorState, render
from twisted.web.test.test_web import DummyRequest
from twisted.web.resource import NoResource
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

    def json(self):
        'Returns JSON'
        return json.dumps(self.as_dict()).encode('utf-8')


class TorResourceWithJson(base.TorResource):
    json_list_class = JsonClass
    json_detail_class = JsonClass


class TestTorResourceBase(unittest.TestCase):

    def setUp(self):
        self.torstate = DummyTorState()
        self.instanceconfig = instanceconfig.TorInstanceConfig()
        self.instanceconfig.state = self.torstate

    def test_set_torstate_afterwards(self):
        '''
        Test if the torstate can be set after 
        constructing an object.
        '''
        resource = TorResourceWithJson()
        self.assertEquals(resource.torstate, None)
        resource.torstate = self.torstate
        self.assertEquals(resource.torstate, self.torstate)

    def test_torstate_in_constructor(self):
        '''
        Test of the torstate can be set in the constructor.
        '''
        resource = TorResourceWithJson(self.instanceconfig)
        self.assertEquals(resource.torstate, self.torstate)

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
            msg = "json_list_class not in error message: " + str(why)
            self.assertTrue('json_list_class' in str(why), msg=msg)

        try:
            TorResourceWithJson2()
            self.fail("No exception thrown for TorResourceWithJson2")
        except RuntimeError as why:
            msg = "json_detail_class not in error message: " + str(why)
            self.assertTrue('json_detail_class' in str(why), msg=msg)

    def test_get_list_notimplemented(self):

        resource = TorResourceWithJson()
        try:
            resource.get_list()
            self.fail("Nothing thrown")
        except NotImplementedError:
            pass

        try:
            resource.get_by_id(0)
            self.fail("Nothing thrown")
        except NotImplementedError:
            pass

    def test_default_detail_class(self):
        class TorResourceWithJson1(TorResourceWithJson):

            def get_by_id(self, ident):
                return ident

        request = DummyRequest([''])
        r = TorResourceWithJson1(self.instanceconfig)
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
        r = TorResourceWithJson1(self.instanceconfig)
        child = r.getChildWithDefault('1', request)
        self.assertIsInstance(child, A)

    def test_invalid_identifier(self):
        class LocalTorResource(TorResourceWithJson):

            def get_by_id(self, ident):
                raise ValueError

        request = DummyRequest([''])
        r = LocalTorResource(self.instanceconfig)
        child = r.getChildWithDefault('1', request)
        self.assertIsInstance(child, NoResource)

    def test_empty_identifier(self):
        parent = self

        class LocalTorResource(TorResourceWithJson):

            def get_by_id(self, ident):
                parent.fail("get_by_id called")

        request = DummyRequest([''])
        r = LocalTorResource(self.instanceconfig)
        child = r.getChildWithDefault('', request)
        self.assertIsInstance(child, NoResource)

    def test_unexisting_identifier(self):

        class LocalTorResource(TorResourceWithJson):

            def get_by_id(self, ident):
                return None

        request = DummyRequest([''])
        r = LocalTorResource(self.instanceconfig)
        child = r.getChildWithDefault('1', request)
        self.assertIsInstance(child, NoResource)

    @inlineCallbacks
    def test_render_list(self):
        class LocalTorResource(TorResourceWithJson):

            def get_list(self):
                return range(100)

        request = DummyRequest([''])
        request.responseCode = 200
        resource = LocalTorResource(self.instanceconfig)
        d = yield render(resource, request)

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

    @inlineCallbacks
    def test_render_list_without_state(self):

        class LocalTorResource(TorResourceWithJson):

            def get_list(self):
                return range(100)

        request = DummyRequest([''])
        request.responseCode = 200
        resource = LocalTorResource()
        d = yield render(resource, request)

        self.assertEquals(request.responseCode, 200,
                          msg=request.responseCode)
        payload = ''.join(request.written)
        payload = json.loads(payload.decode('utf-8'))
        self.assertIsInstance(payload, dict)
        self.assertTrue('error' in payload, msg=payload)

    def test_get_child_without_state(self):
        class LocalTorResource(TorResourceWithJson):

            def get_by_id(self, ident):
                raise RuntimeError("called")

        request = DummyRequest([''])
        request.responseCode = 200
        resource = LocalTorResource()
        child = resource.getChildWithDefault('1', request)
        self.assertIsInstance(child, response.JsonError)


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
