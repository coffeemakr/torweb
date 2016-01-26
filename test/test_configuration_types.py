#!/usr/bin/env python
# coding=utf-8

from twisted.trial import unittest

from torweb import configuration


class TestConfigurationTypeBoolean(unittest.TestCase):

    def test_values(self):
        entry = configuration.BooleanEntry()
        self.assertIs(entry.load(1), True)
        self.assertIs(entry.load(True), True)
        self.assertIs(entry.load('True'), True)
        self.assertIs(entry.load('true'), True)
        self.assertIs(entry.load(False), False)
        self.assertIs(entry.load(0), False)
        self.assertIs(entry.load('0'), False)
        self.assertIs(entry.load('False'), False)

    def test_invalid_values(self):
        entry = configuration.BooleanEntry()
        for value in ['', 2, -1, None, [], [1,2,3,4], dict(), {'hi': 'hello'},
                      0.5, -0.5]:
            self.assertRaises(ValueError, entry.load, value)

class TestConfigurationTypeString(unittest.TestCase):

    def test_values(self):
        entry = configuration.StringEntry()
        self.assertEquals(entry.load('1'), u'1')
        self.assertEquals(entry.load('Hello'), u'Hello')
        self.assertEquals(entry.load(u'Ünicöde'), u'Ünicöde')
        self.assertEquals(entry.load('\xc3\x9cnic\xc3\xb4de'), u'Ünicôde')
        self.assertEquals(entry.load(b'\xc3\x9cnic\xc3\xb4de'), u'Ünicôde')
        self.assertEquals(entry.load('Some longer text ' * 100),
                                     u'Some longer text ' * 100)
        self.assertEquals(entry.load(''), u'')

    def test_invalid_values(self):
        entry = configuration.StringEntry()
        for value in [None, [], [1,2,3,4], dict(), 1, -1 ,0.5, -0.5]:
            self.assertRaises(ValueError, entry.load, value)

    def test_default(self):
        entry = configuration.StringEntry()
        self.assertEquals(entry.get_default(), None)

class TestConfigurationTypeInteger(unittest.TestCase):

    def test_values(self):
        entry = configuration.IntegerEntry()
        self.assertEquals(entry.load(-1), -1)
        self.assertEquals(entry.load(0), 0)
        self.assertEquals(entry.load(1), 1)
        self.assertEquals(entry.load(2**10), 2**10)

    def test_invalid_values(self):
        entry = configuration.IntegerEntry()
        self.assertRaises(ValueError, entry.load, None)
        self.assertRaises(ValueError, entry.load, [])
        self.assertRaises(ValueError, entry.load, [1,2,3,4])
        self.assertRaises(ValueError, entry.load, dict())
        self.assertRaises(ValueError, entry.load, 0.5)
        self.assertRaises(ValueError, entry.load, -0.5)
        self.assertRaises(ValueError, entry.load, 'NaN')
        self.assertRaises(ValueError, entry.load, 'Some text')
        self.assertRaises(ValueError, entry.load, u'some ünicôde text')
        self.assertRaises(ValueError, entry.load, '1')
        self.assertRaises(ValueError, entry.load, '0')
        self.assertRaises(ValueError, entry.load, u'1')
        self.assertRaises(ValueError, entry.load, u'0')


class TestConfigurationTypeDict(unittest.TestCase):

    def test_empty_dict(self):
        entry = configuration.DictEntry({})
        self.assertEquals(entry.load({}), {})
        self.assertRaises(ValueError, entry.load, {'something': 1})
        self.assertRaises(ValueError, entry.load, {1: 0})

    def test_value_checks(self):
        entry = configuration.DictEntry({
            'integer': configuration.IntegerEntry(),
            'string': configuration.StringEntry()
        })
        value = {'integer': 0, 'string': 'hello'}
        self.assertEqual(entry.load(value), value)
        value = {'integer': 'NaN', 'string': 'hello'}
        self.assertRaises(ValueError, entry.load, value)
        value = {'integer': 0, 'string': 0xFF}
        self.assertRaises(ValueError, entry.load, value)

    def test_nested_value_checks(self):
        entry = configuration.DictEntry({
            'dict': configuration.DictEntry({
                'integer': configuration.IntegerEntry(),
                'string': configuration.StringEntry()
            })
        })
        value = {'dict': {'integer': 0, 'string': 'hello'}}
        self.assertEqual(entry.load(value), value)
        value = {'dict': {'integer': 'NaN', 'string': 'hello'}}
        self.assertRaises(ValueError, entry.load, value)
        value = {'dict': {'integer': 0, 'string': 0xFF}}
        self.assertRaises(ValueError, entry.load, value)
        value = {'integer': 0, 'string': 'hello'}
        self.assertRaises(ValueError, entry.load, value)

    def test_default_value(self):
        entry = configuration.DictEntry({
            'dict': configuration.DictEntry({
                'integer': configuration.IntegerEntry(default_value=1),
                'string': configuration.StringEntry(default_value='def')
            })
        })

        self.assertEqual(entry.get_default(), {
            'dict': {
                'integer': 1,
                'string': 'def'
            }
        })

    def test_invalid_values(self):
        entry = configuration.DictEntry({})
        self.assertRaises(ValueError, entry.load, None)
        self.assertRaises(ValueError, entry.load, [])
        self.assertRaises(ValueError, entry.load, [1,2,3,4])
        self.assertRaises(ValueError, entry.load, 0.5)
        self.assertRaises(ValueError, entry.load, -0.5)
        self.assertRaises(ValueError, entry.load, 'NaN')
        self.assertRaises(ValueError, entry.load, 'Some text')
        self.assertRaises(ValueError, entry.load, u'some ünicôde text')
        self.assertRaises(ValueError, entry.load, '1')
        self.assertRaises(ValueError, entry.load, '0')
        self.assertRaises(ValueError, entry.load, u'1')
        self.assertRaises(ValueError, entry.load, u'0')


class TestConfigurationTypeList(unittest.TestCase):
    def test_empty_list(self):
        entry = configuration.ListEntry(configuration.IntegerEntry())
        self.assertEqual(entry.load([]), [])

    def test_type_checking(self):
        entry = configuration.ListEntry(configuration.IntegerEntry())
        self.assertRaises(ValueError, entry.load, ['hi',1,2,3,4])
        self.assertRaises(ValueError, entry.load, [1,2,3,4,'hi'])
        self.assertRaises(ValueError, entry.load, [1,2,3,'hi',1,2,3])


    def test_default_value(self):
        entry = configuration.ListEntry(configuration.IntegerEntry())
        self.assertEqual(entry.get_default(), [])
