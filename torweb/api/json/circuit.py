import json
import datetime
import txtorcon

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
            result[attr] = value
        return result

    def json(self):
        return json.dumps(self.as_dict()).encode('utf8') 

class JsonRouter(JsonObject):
    attributes = (
        'name',
        'unique_name',
        'modified',
        'location',
        'flags',
        'bandwidth',
        'policy',
        'ip'
    )

class JsonCircuit(JsonObject):

    attributes = (
        'id',
        'state',
        'purpose',
        'path',
#        'is_built'
    )
        
    def get_path(self, path):
        result = []
        if self.txtor is not None:
            for router in path:
                print(dir(router))
                result.append(JsonRouter(router).as_dict())
        return result

    def as_dict(self):
        result = super(JsonCircuit, self).as_dict()
        result['path'] = self.get_path(result['path'])
        return result

class JsonCircuitDetails(JsonCircuit):
    
    attributes = (
        'id',
        'status',
        'path',
        'build_flags',
        'purpose',
        'hs_state',
        'rend_query',
        'created',
        'reason',
        'remote_reason',
        'socks_username',
        'socks_password',
    )