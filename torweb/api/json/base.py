# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

import json
import datetime
import txtorcon
from txtorcon.util import ipaddr as ipaddress

__all__ = ('JsonObject',)


IPADDRESSES = (ipaddress.IPv4Address,
               ipaddress.IPv6Address,
               ipaddress.IPAddress)


class JsonObject(object):
    '''
    Base class for serializeable object wrappers.
    '''
    #: List or tuple of tuples with two values:
    #: The old and the new attribute name.
    rename = ()

    #: All names of attributes to copy into the json dictionary
    attributes = ()

    def __init__(self, obj):
        self.object = obj

    def as_dict(self):
        '''
        Returns a dictionary of all :attr:`attributes`.
        '''
        result = {}
        for attr in self.attributes:
            value = getattr(self.object, attr)
            if isinstance(value, datetime.datetime):
                value = value.isoformat()
            elif isinstance(value, txtorcon.util.NetLocation):
                # TODO: Use existing information in value
                value = {'country': value.countrycode}
            elif type(value) in IPADDRESSES:
                value = value.exploded
            result[attr] = value
        for old, new in self.rename:
            if old in result:
                result[new] = result.pop(old)
        return result

    def json(self):
        '''
        Returns the dictionary as a JSON string.
        This method calls :meth:`as_dict` and converts the result into a json
        value.
        '''
        return json.dumps(self.as_dict()).encode('utf8')
