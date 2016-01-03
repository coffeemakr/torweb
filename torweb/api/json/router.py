# -*- coding: utf-8 -*-
'''
JSON router wrapper
'''
from __future__ import absolute_import, print_function, with_statement

from .base import JsonObjectWrapper

__all__ = ('JsonRouterMinimal', 'JsonRouter')


class JsonRouter(JsonObjectWrapper):
    '''
    JSON wrapper for Router
    '''

    attributes = (
        'name',
        'unique_name',
        'modified',
        'location',
        'flags',
        'bandwidth',
        'policy',
        'ip',
        'id_hex'
    )

    def as_dict(self):
        result = super(JsonRouter, self).as_dict()
        result['id'] = result.pop('id_hex')[1:]
        return result


class JsonRouterMinimal(JsonRouter):
    '''
    Minimal JSON wrapper for router.
    '''

    attributes = (
        'name',
        'id_hex',
        'ip',
        'location'
    )
