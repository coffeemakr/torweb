import json
import datetime

class JsonObject(object):
    def __init__(self, stem=None, txtor=None):
        self.stem = stem
        self.txtor = txtor

    def as_dict(self):
        result = {}
        if self.txtor is not None:
            obj = self.txtor
            obj_attrs = self.txtor_attributes
        else:
            obj = self.stem
            obj_attrs = self.stem_attributes

        for i, attr in enumerate(self.json_attributes):
            value = getattr(obj, obj_attrs[i])
            if isinstance(value, datetime.datetime):
                value = value.isoformat()
            result[attr] = value
        return result

    def json(self):
        return json.dumps(self.as_dict()).encode('utf8') 

class JsonRouter(JsonObject):
    json_attributes = (
        'fingerprint',
        'name',
        'flags'
    )
    stem_attributes = (
        'fingerprint',
        'name',
        'flags'
    )
    txtor_attributes = (
        'unique_name',
        'name',
        'flags'
    )

class JsonCircuit(JsonObject):

    json_attributes = (
        'id',
        'status',
        'purpose',
        'path'
    )

    stem_attributes = (
        'id',
        'status',
        'purpose',
        'path'
    )
    txtor_attributes = (
        'id',
        'state',
        'purpose',
        'path'
    )
        
    def get_path(self, path):
        result = []
        if self.txtor is not None:
            for router in path:
                result.append(JsonRouter(txtor=router).as_dict())
        else:
            for fingerprint, name in path:
                result.append({
                    'fingerprint': fingerprint,
                    'name': name
                })
        return result

    def as_dict(self):
        result = super(JsonCircuit, self).as_dict()
        result['path'] = self.get_path(result['path'])
        return result

class JsonCircuitDetails(JsonCircuit):
    json_attributes = (
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
    stem_attributes = json_attributes
