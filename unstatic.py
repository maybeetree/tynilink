import cherrypy
from base64 import b64encode as b64e

from funcs import *

'''missing description'''

class unstatic:
    '''@cherrypy.expose
    def homepage(self):
        return open('templates/homepage.html').read() % open(
            'templates/create_url.html').read()'''

    @cherrypy.expose
    def sucsess(self,surl='',lurl=''):
        '''when user added url sucsessfully'''
        
        ses_log('[added link]', 'sending page')
        ses_log('[...END SESSION!!...]', '')
        
        return open(
            'templates/info/link/created_url.html'
            ).read() % (surl,base64.b64decode(lurl))

    @cherrypy.expose
    def auth(self,dest):
        return open('templates/info/link/auth.html').read() % dest

    '''@cherrypy.expose
    def rnd_grad(self):
        cherrypy.response.headers['Content-Type'] = "text/css"
        return rnd_grad_f()'''

    #@cherrypy.expose
    #def whatisthis(self):
    #    return open(
    #        'templates/whatisthis.html'
    #        ).read() % open(
    #            'templates/create_url.html').read()
