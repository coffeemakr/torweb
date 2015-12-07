import os
import cherrypy
import mimetypes

mimetypes.init()

class StaticContentHandler(object):
    def __init__(self, basepath):
        self.basepath = os.path.abspath(basepath)
    
    def is_safe(self, path):
        path = os.path.abspath(path)
        return path.startswith(self.basepath)

    @classmethod
    def from_relative(cls, script, path):
        path = os.path.join(os.path.split(script)[0], path)
        return cls(path)

    def _set_mime(self, path):
        mime, _ = mimetypes.guess_type(path)
        if mime is not None:
            cherrypy.response.headers['Content-Type'] = str(mime) + ';charset=utf-8'

    def GET(self, *path, **kwargs):        
        if not path:
            path = ('index.html',)
        path = os.path.join(*path)
        path = os.path.join('app', path)
        if not self.is_safe(path):
            raise cherrypy.HTTPError(404)
        if not os.path.isfile(path):
            raise cherrypy.HTTPError(404, path)
        self._set_mime(path)
        with open(path, 'rb') as f:
            return f.read()