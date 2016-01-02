# -*- coding: utf-8 -*-
'''
JSON circuit wrappers
'''
from __future__ import absolute_import, print_function, with_statement

from .router import JsonRouterMinimal
from .base import JsonObject

__all__ = ('JsonCircuitMinimal', 'JsonCircuit')


class JsonCircuit(JsonObject):
    '''
    Serializable wrapper for Circuit
    '''

    attributes = (
        'id',
        'state',
        'purpose',
        'path',
        'build_flags',
        'time_created'
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
