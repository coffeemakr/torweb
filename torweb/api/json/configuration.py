# -*- coding: utf-8 -*-
'''
JSON Configuration wrappers
'''
from __future__ import absolute_import, print_function, with_statement

from .base import JsonObject

__all__ = ('JsonConfig', 'JsonConfigMinimal')


class JsonConfig(JsonObject):
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
