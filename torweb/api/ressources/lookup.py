from twisted.web import resource
from torweb.api.util import response
import socket

class DNSRoot(resource.Resource):
	def __init__(self):
		resource.Resource.__init__(self)
		self.putChild('reverse', ReverseDNSRoot())

class ReverseDNSRoot(resource.Resource):
	def getChild(self, ip, request):
		return ReverseDNS(ip)

class ReverseDNS(resource.Resource):
	def __init__(self, ip):
		self.ip = ip
	
	def lookup(self):
		host = None
		alias = None
		ips = []
		try:
	 		host, alias, ips = socket.gethostbyaddr(self.ip)
		except socket.error:
			pass

		return {
			'host': host,
			'alias': alias,
			'ips': ips
		}
	
	@response.json
	def render_GET(self, path):
		return self.lookup()
