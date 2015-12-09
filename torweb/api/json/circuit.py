from .router import JsonRouter
from .base import JsonObject

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
                result.append(JsonRouter(router).as_dict())
        return result

    def as_dict(self):
        result = super(JsonCircuit, self).as_dict()
        result['path'] = self.get_path(result['path'])
        return result

class JsonCircuitDetails(JsonCircuit):
    
    attributes = (
        'id',
        'state',
        'purpose',
        'path',
        'build_flags',
        'time_created'
    )