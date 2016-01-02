# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement


import json
import datetime
import txtorcon
from txtorcon.util import ipaddr as ipaddress

from torweb.api.util import geoip

__all__ = ('JsonObject',)


IPADDRESSES = (ipaddress.IPv4Address,
               ipaddress.IPv6Address,
               ipaddress.IPAddress)


class JsonObject(object):

    rename = ()

    def __init__(self, obj):
        self.object = obj

    def as_dict(self):
        result = {}
        for attr in self.attributes:
            value = getattr(self.object, attr)
            if isinstance(value, datetime.datetime):
                value = value.isoformat()
            elif isinstance(value, txtorcon.util.NetLocation):
                # TODO: Use existing information in value
                value = {'country': value.countrycode}
                value['country_name'] = geoip.get_country_name(value[
                                                               'country'])
            elif type(value) in IPADDRESSES:
                value = value.exploded
            result[attr] = value
        for old, new in self.rename:
            if old in result:
                result[new] = result.pop(old)
        return result

    def json(self):
        return json.dumps(self.as_dict()).encode('utf8')
