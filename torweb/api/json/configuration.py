# -*- coding: utf-8 -*-
'''
JSON Configuration wrappers
'''
from __future__ import absolute_import, print_function, with_statement

from .base import JsonObjectWrapper

__all__ = ('JsonConfig', 'JsonConfigMinimal')


class JsonConfig(JsonObjectWrapper):
    '''
    Convert config entry to json
    '''
    attributes = ('id', 'value', 'value_type')
    rename = (('value_type', 'type'),)


class JsonConfigMinimal(JsonConfig):
    '''
    Convert config entry to minmal json
    '''
    attributes = ('id', 'value')
