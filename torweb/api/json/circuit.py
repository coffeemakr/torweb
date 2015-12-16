from .router import JsonRouterMinimal
from .base import JsonObject

__all__ = ('JsonCircuitMinimal', 'JsonCircuit')
        

class JsonCircuit(JsonObject):

    attributes = (
        'id',
        'state',
        'purpose',
        'path',
        'build_flags',
        'time_created'
    )

    def get_path(self, path):
        result = []
        if self.txtor is not None:
            for router in path:
                result.append(JsonRouterMinimal(router).as_dict())
        return result

    def as_dict(self):
        result = super(JsonCircuit, self).as_dict()
        result['path'] = self.get_path(result['path'])
        return result
    


class JsonCircuitMinimal(JsonCircuit):
    attributes = (
        'id',
        'state',
        'purpose',
        'path',
    )