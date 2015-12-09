from .base import JsonObject
from .circuit import JsonCircuit
__all__ = ('JsonStream',)

class JsonStream(JsonObject):
	attributes = (
		'id',
		'state',
		'target_host',
		'target_addr',
		'target_port',
		'source_addr',
		'source_port',
		'circuit'
	)

	def as_dict(self):
		result = super(JsonStream, self).as_dict()
		if result['circuit'] is not None:
			result['circuit'] = JsonCircuit(result['circuit']).as_dict()
		return result;