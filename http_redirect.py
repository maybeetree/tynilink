import cherrypy

class redirect:
    @cherrypy.expose
    def index(*args):
        raise cherrypy.HTTPRedirect('https://localhost:443')
