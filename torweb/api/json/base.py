import json
import datetime
import txtorcon
try:
    import ipaddress
except ImportError:
    from txtorcon.util import ipaddr as ipaddress

class JsonObject(object):
    def __init__(self, txtor):
        self.txtor = txtor

    def as_dict(self):
        result = {}
        obj = self.txtor
        for attr in self.attributes:
            value = getattr(obj, attr)
            if isinstance(value, datetime.datetime):
                value = value.isoformat()
            elif isinstance(value, txtorcon.util.NetLocation):
                value = {'cc': value.countrycode}
            elif type(value) in (ipaddress.IPv4Address, ipaddress.IPv6Address, ipaddress.IPAddress):
                value = value.exploded
            result[attr] = value
        return result

    def json(self):
        return json.dumps(self.as_dict()).encode('utf8') 