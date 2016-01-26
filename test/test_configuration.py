#!/usr/bin/env python
# coding=utf-8

import json
import tempfile

from twisted.trial import unittest

from torweb import configuration


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        self.entry = configuration.DictEntry({
            'number': configuration.IntegerEntry(),
            'text': configuration.StringEntry(),
            'dict': configuration.DictEntry({
                'number': configuration.IntegerEntry(),
                'text': configuration.StringEntry()
            })
        })
        self.config = configuration.Configuration(root_entry=self.entry)

    def test_empty_configuration(self):
        default = {
            'number': None,
            'text': None,
            'dict': {
                'number': None,
                'text': None
            }
        }
        self.assertEqual(self.config.value, default)

    def test_read_file(self):
        data = {
            'number': 1,
            'text': 'hi threre',
            'dict': {
                'number': 2,
                'text': 'some other \n text'
            }
        }
        temp = tempfile.NamedTemporaryFile()
        json.dump(data, temp)
        temp.flush()

        self.config.read_file(temp.name)

        self.assertEqual(self.config.value, data)
        temp.close()

    def test_read_invalid_data_from_file(self):
        data = {
            'number': 'hi',
            'text': 'hi threre',
            'dict': {
                'number': 2,
                'text': 'some other \n text'
            }
        }
        temp = tempfile.NamedTemporaryFile()
        json.dump(data, temp)
        temp.flush()

        self.assertRaises(ValueError, self.config.read_file, temp.name)
        temp.close()
