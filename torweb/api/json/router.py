from .base import JsonObject

class JsonRouter(JsonObject):
    attributes = (
        'name',
        'unique_name',
        'modified',
        'location',
        'flags',
        'bandwidth',
        'policy',
        'ip',
        'id_hex'
    )
    def as_dict(self):
        result = super(JsonRouter, self).as_dict()
        result['id'] = result.pop('id_hex')[1:]
        return result