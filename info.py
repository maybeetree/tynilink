import cherrypy

from funcs import *

'''these are pages for displaying info for user'''

class info:
    @cherrypy.expose
    def index(self):
        return 'no index'

    @cherrypy.expose
    def whatisthis(self):
        return open('templates/whatisthis.html').read()

    @cherrypy.expose
    def Wrong_password(self,surl='',lurl='',user=''):
        return 'wrong pass'

    @cherrypy.expose
    def Unknown_user(self,surl='',lurl='',user=''):
        return 'unknown user'

    @cherrypy.expose
    def url_taken(self,surl='',lurl='',user=''):
        return 'short url already taken!'

    
