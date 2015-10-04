import cherrypy

class intro:
    @cherrypy.expose
    def index(self):
        return open('templates/whatisthis.html').read()
