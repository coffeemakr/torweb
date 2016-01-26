# -*- coding: utf-8 -*-
'''
JSON circuit wrappers
'''
from __future__ import absolute_import, print_function, with_statement

from .base import JsonObjectWrapper
from .minimalstream import JsonStreamMinimal
from .router import JsonRouterMinimal

__all__ = ('JsonCircuitMinimal', 'JsonCircuit')


class JsonCircuit(JsonObjectWrapper):
    '''
    Serializable wrapper for Circuit
    '''

    attributes = (
        'id',
        'state',
        'purpose',
        'path',
        'build_flags',
        'time_created',
        'streams'
    )

    @staticmethod
    def get_path(path):
        '''
        Returns a list of all routers in path.
        '''
        result = []
        for router in path:
            result.append(JsonRouterMinimal(router).as_dict())
        return result

    def as_dict(self):
        result = super(JsonCircuit, self).as_dict()
        result['path'] = JsonCircuit.get_path(result['path'])
        if 'streams' in result:
            streams = []
            for stream in result['streams']:
                streams.append(JsonStreamMinimal(stream).as_dict())
            result['streams'] = streams
        return result


class JsonCircuitMinimal(JsonCircuit):
    '''
    Minimal wrapper for a circuit.
    '''
    attributes = (
        'id',
        'state',
        'purpose',
        'path',
    )
