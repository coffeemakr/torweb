from twisted.web import resource
from torweb.api.util import response
import stem
from torweb.api.json import JsonCircuit, JsonCircuitDetails

class TorResource(resource.Resource):

	def get_torstate(self):
		return self._torstate

	def set_torstate(self, torstate):
		self._torstate = torstate

	torstate = property(get_torstate)

	def __init__(self, torstate=None):
		resource.Resource.__init__(self)
		self._torstate = torstate

class CircuitRoot(TorResource):
	def getChild(self, path, request):
		if not path:
			return CircuitList(self.torstate)
		try:
			print path
			return Circuit(self.torstate.circuits[int(path)])
		except KeyError, ValueError:
			return resource.NoResource("No such circuit.")

class CircuitList(TorResource):
	
	@response.json
	def render_GET(self, request):
		result = []
		for c in self.torstate.circuits.values():
			result.append(JsonCircuit(c).as_dict())
		return result

class Circuit(resource.Resource):

	isLeaf = True

	def __init__(self, circuit):
		resource.Resource.__init__(self)
		self.circuit = circuit

	def render_GET(self, request):
		return JsonCircuitDetails(self.circuit).json()
	
	@response.json
	def render_DELETE(self, request):
		self.circuit.close()
		return {}

