import datetime
import json

import txtorcon.util
from torweb.api.json import (base, circuit, minimalstream,
                             router)
from txtorcon.util import ipaddr as ipaddress

from txtorcon import Router, Circuit, Stream

IPADDRESSES = (ipaddress.IPv4Address,
               ipaddress.IPv6Address,
               ipaddress.IPAddress)


__all__ = ['ExtendedJSONEncoder']


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
        if base.IJSONSerializable.providedBy(o):
            return base.IJSONSerializable(o).as_dict()
        elif isinstance(o, Router):
            return router.JsonRouterMinimal(o).as_dict()
        elif isinstance(o, Circuit):
            return circuit.JsonCircuitMinimal(o).as_dict()
        elif isinstance(o, Stream):
            return minimalstream.JsonStreamMinimal(o).as_dict()
        elif isinstance(o, datetime.datetime):
            return o.isoformat()
        elif isinstance(o, txtorcon.util.NetLocation):
            return {'country': o.countrycode}
        elif isinstance(o, IPADDRESSES):
            return o.exploded
        return json.JSONEncoder.default(self, o)
