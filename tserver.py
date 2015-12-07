from twisted.web import server, resource, http, static, util
from twisted.internet.endpoints import TCP4ClientEndpoint
from api.ressources.circuit import CircuitRoot
import api.websocket
from stem.control import Controller
import txtorcon



class RootResource(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild('', util.Redirect('/app'))
        self.putChild('app', static.File('app'))
        self.putChild('api', ApiRessource())


class ApiRessource(resource.Resource):
    '''
    RESTful API definition.
    '''
    def __init__(self):
        resource.Resource.__init__(self)
        port = 9151
        self.controller = Controller.from_port(port=port)
        connection = TCP4ClientEndpoint(reactor, "localhost", port)
        self.controller.authenticate()
        self.putChild('circuit', CircuitRoot(self.controller))
        self.putChild('websocket', api.websocket.get_ressource(connection))

if __name__ == "__main__":
    import sys
    from twisted.internet import reactor
    from twisted.python import log
    import sys
    log.startLogging(sys.stdout)
    #messageStore = message.MessageStore(sys.argv[1])
    reactor.listenTCP(8082, server.Site(RootResource()))
    reactor.run()