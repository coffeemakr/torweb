import os

from twisted.trial import unittest

from torweb import data

class TestAppPath(unittest.TestCase):
    def setUp(self):
        self.data_path = os.path.split(__file__)[0]
        self.data_path = os.path.join(self.data_path, '..', 'torweb', 'data')
        self.data_path = os.path.abspath(self.data_path)

    def test_path(self):
        self.assertEqual(self.data_path, data.get_path())

    def test_app_path(self):
        path = os.path.join(self.data_path, 'app')
        self.assertEqual(path, data.get_app_dir())

    def test_default_config(self):
        path = os.path.join(self.data_path, 'config', 'default.json')
        self.assertEqual(path, data.default_configuration())
