# -*- coding: utf-8 -*-
'''
All Exceptions
'''


class TorwebError(Exception):
    '''
    Base exception for all torweb errors.
    '''
    pass


class ConfigurationError(TorwebError):
    '''
    The configuration caused an error.
    '''
    pass
