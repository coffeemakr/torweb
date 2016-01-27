import datetime
import json

from txtorcon.util import ipaddr as ipaddress
import txtorcon.util

from .base import IJSONSerializable

IPADDRESSES = (ipaddress.IPv4Address,
               ipaddress.IPv6Address,
               ipaddress.IPAddress)

__all__ = ['JSONEncoder']


class ExtendedJSONEncoder(json.JSONEncoder):
    '''
    Customized JSON encoder which handels the following objects:
      * Implementations of :class:`IJSONSerializable`
      * :class:`txtorcon.util.NetLocation`
      * :class:`txtorcon.util.ipaddr.IPv4Address`
      * :class:`txtorcon.util.ipaddr.IPv6Address`
      * :class:`txtorcon.util.ipaddr.IPAddress`
    '''
    def default(self, o):
        '''
        Implementation of encoding
        '''
        if IJSONSerializable.providedBy(o):
            return IJSONSerializable(o).as_dict()
        elif isinstance(o, datetime.datetime):
            return o.isoformat()
        elif isinstance(o, txtorcon.util.NetLocation):
            return {'country': o.countrycode}
        elif isinstance(o, IPADDRESSES):
            return o.exploded
        return json.JSONEncoder.default(self, o)
