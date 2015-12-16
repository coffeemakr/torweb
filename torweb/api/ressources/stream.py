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
			id = int(id)
		except ValueError:
			return resource.NoResource("Invalid ID.")

		if id in self.torstate.streams:
			try:
				return Stream(self.torstate.streams[id])
			except KeyError:
				pass

		return resource.NoResource(repr(self.torstate.streams.keys()))


class StreamList(TorResource):

	isLeaf = True

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