from twisted.web import server, resource, http, static, util
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from torweb.api.ressources import CircuitRoot, RouterRoot, StreamRoot, DNSRoot
import torweb.api.websocket
from stem.control import Controller
import txtorcon
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
        tor_connection = txtorcon.build_tor_connection(connection)

        self.circuitRoot = CircuitRoot()
        self.routerRoot = RouterRoot()
        self.streamRoot = StreamRoot()
        tor_connection.addCallback(self.txtorCallback)

        self.putChild('circuit', self.circuitRoot)
        self.putChild('router', self.routerRoot)
        self.putChild('stream', self.streamRoot)
        self.websocket = torweb.api.websocket.get_ressource(connection)
        self.putChild('websocket', self.websocket)
        self.putChild('dns', DNSRoot())

    def txtorCallback(self, state):
        self.circuitRoot.set_torstate(state)
        self.routerRoot.set_torstate(state)
        self.streamRoot.set_torstate(state)
    
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