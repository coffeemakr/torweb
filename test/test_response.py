# -*- coding: utf-8 -*-

from twisted.trial import unittest

from torweb.api.util import response
from twisted.web.test.test_web import DummyRequest
import json


def _render(resource, request):
    result = resource.render(request)
    if isinstance(result, str):
        request.write(result)
        request.finish()
        return succeed(None)
    elif result is server.NOT_DONE_YET:
        if request.finished:
            return succeed(None)
        else:
            return request.notifyFinish()
    else:
        raise ValueError("Unexpected return value: %r" % (result,))


class TestJsonResponse(unittest.TestCase):

    def setUp(self):
        self.request = DummyRequest([''])
        self.request.requestHeaders.addRawHeader(
            'accept', 'application/json;charset=utf-8')

    def tearDown(self):
        pass

    def test_dict_reponse(self):
        @response.encode
        def valid_dict_answer(*args):
            return {'value1': 1, u'valü': 'unicöde', 1: 2, 2: None, 3: [1, 2, 3]}

        payload = valid_dict_answer(self.request)
        self.assertIsInstance(payload, str, "Not a string returned")
        content = json.loads(payload.decode('utf-8'))
        self.assertIsInstance(content, dict)
        self.assertTrue('value1' in content)
        self.assertEquals(content['value1'], 1)
        self.assertTrue(u'valü' in content)
        self.assertEquals(content[u'valü'], u'unicöde')
        self.assertTrue('1' in content)
        self.assertEquals(content['1'], 2)
        self.assertTrue('2' in content)
        self.assertEquals(content['2'], None)
        self.assertTrue('3' in content)
        self.assertIsInstance(content['3'], list)
        self.assertTrue(len(content['3']) == 3)
