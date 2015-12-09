from twisted.web import resource
from .base import TorResource
from torweb.api.util import response
from torweb.api.json import JsonStream

__all__ = ('StreamRoot',)

class StreamRoot(TorResource):
	def getChild(self, id, request):
		if not id:
			return StreamList(self.torstate)
		try:
			return Stream(self.torstate.streams[id])
		except KeyError, ValueError:
			raise
			return resource.NoResource("No such stream.")


class StreamList(TorResource):
	
	@response.json
	def render_GET(self, request):
		result = []
		for c in self.torstate.streams.values():
			result.append(JsonStream(c).as_dict())
		return result

class Stream(resource.Resource):

	isLeaf = True

	def __init__(self, stream):
		resource.Resource.__init__(self)
		self.stream = stream

	@response.json
	def render_GET(self, request):
		return JsonStream(self.stream).json()

	@response.json
	def render_DELETE(self, request):
		self.stream.close()
		return {}		