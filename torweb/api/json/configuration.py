# -*- coding: utf-8 -*-
'''
JSON Configuration wrappers
'''
from __future__ import absolute_import, print_function, with_statement

from .base import JsonObjectWrapper

__all__ = ('JsonConfig', 'JsonConfigMinimal')


class JsonConfigMinimal(JsonObjectWrapper):
    '''
    Convert config entry to minmal json
    '''
    attributes = ('id', 'value')


class JsonConfig(JsonConfigMinimal):
    '''
    Convert config entry to json
    '''
    attributes = ('id', 'value', 'value_type', 'is_list')
    rename = (('value_type', 'type'),)

    def as_dict(self):
        result = super(JsonConfig, self).as_dict()
        result['type'] = result['type'].__name__
        return result
