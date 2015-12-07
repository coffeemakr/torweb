from twisted.web import resource
from api.util import response
import stem
from api.json import JsonCircuit

class TorResource(resource.Resource):

	def check_controller(self):
		return self._controller

	def get_contoller(self):
		return self._controller

	def set_controller(self, controller):
		self._controller = controller

	controller = property(get_contoller, set_controller)

	def __init__(self, controller):
		resource.Resource.__init__(self)
		self.set_controller(controller)


class CircuitRoot(TorResource):
	def getChild(self, path, request):
		if not path:
			return CircuitList(self.controller)
		try:
			print path
			return Circuit.from_id(path, controller=self.controller)
		except ValueError:
			return resource.NoResource("No such circuit.")

class CircuitList(TorResource):
	@response.json
	def render_GET(self, request):
		result = []
		for c in self.controller.get_circuits():
			result.append(JsonCircuit.from_stem(c))
		return result

class Circuit(TorResource):

	isLeaf = True

	def __init__(self, circuit, controller):
		TorResource.__init__(self, controller)
		self.circuit = circuit

	@classmethod
	def from_id(cls, id, controller):
		circuit = controller.get_circuit(id)
		return cls(circuit, controller)

	def as_dict(self):
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
		result = response.object_to_dict(self.circuit, attributes)
		result['path'] = path_to_dict(result['path'])
		return result

	@response.json
	def render_GET(self, request):
		return self.as_dict()
	
	@response.json
	def render_DELETE(self, request):
		error = False;
		try:
			self.controller.close_circuit(self.circuit.id)
		except stem.InvalidArguments:
			return resource.NoResource()
		except stem.InvalidRequest:
			error = True
		return {'success': not error}
