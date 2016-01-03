# -*- coding: utf-8 -*-
'''
Minimal JSON stream wrapper. This is in a different file
than :class:`JsonStream` so :class:`JsonCircuit` can use this
without dependency issues.
'''
from __future__ import absolute_import, print_function, with_statement

from .base import JsonObjectWrapper

__all__ = ('JsonStreamMinimal', )


class JsonStreamMinimal(JsonObjectWrapper):
    '''
    Json wrapper for stream objects.
    '''

    attributes = (
        'id',
        'state',
        'target_host',
        'target_addr',
        'target_port',
        'source_addr',
        'source_port'
    )
