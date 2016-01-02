from twisted.internet.defer import succeed
from twisted.web import server
from twisted.names import client
import subprocess
import os


def render(resource, request):
    result = resource.render(request)
    if isinstance(result, str):
        request.write(result)
        request.finish()
        return succeed(None)
    elif result is server.NOT_DONE_YET:
        if request.finished:
            return succeed(None)
        else:
            return request.notifyFinish()
    else:
        raise ValueError("Unexpected return value: %r" % (result,))


class DummyTorState(object):
    
    routers_by_hash = {}
    routers_by_name = {}
    routers = {}

    def __init__(self):
        pass


class TorProcess(object):
    def __init__(self, rc='torrc'):
        basedir = os.path.split(__file__)[0]
        self.torrc = os.path.join(basedir, rc) 
        self.proc = subprocess.Popen(['tor', '-f', self.torrc])
        
    def end(self):
        self.proc.terminate()
        self.proc.wait()
