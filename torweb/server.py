from twisted.web import server, resource, http, static, util
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from torweb.api.ressources.circuit import CircuitRoot
import torweb.api.websocket
from stem.control import Controller

import os
class RootResource(resource.Resource):
    def __init__(self, basedir):
        resource.Resource.__init__(self)
        self.putChild('', util.Redirect('/app'))
        self.putChild('app', static.File(os.path.abspath(os.path.join(basedir, 'app'))))
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
        self.putChild('websocket', torweb.api.websocket.get_ressource(connection))

def main():
    import sys
    from twisted.python import log
    import sys
    log.startLogging(sys.stdout)
    #messageStore = message.MessageStore(sys.argv[1])
    reactor.listenTCP(8082, server.Site(RootResource(os.path.join(os.path.split(__file__)[0], '..'))))
    reactor.run()

if __name__ == "__main__":
    main()