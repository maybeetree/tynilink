import MySQLdb as mdb
import StringIO
import qrcode
import hashlib, base64

import cherrypy
from cherrypy.lib import cptools
from cherrypy.lib import auth_basic
from cherrypy.lib.static import serve_fileobj
import socket

import os
from time import sleep, ctime
from random import randint
import sys

from funcs import *

'''these are the maintainance pages'''

class utils:
    '''accsessing logs, etc. from browser'''

    def __init__(self):
        global cur, con

        ses_log('[ut init]', 'init done')
        self.cur = cur
        self.con = con

    @cherrypy.expose
    def index(self):
        ses_log('[---ut session begin---]', '')
        ses_log('[ut index]', 'sending index')
        ses_log('[___ut session end___]', '')
        return 'hello'

    @cherrypy.expose
    def all_urls(self, limit = 10):
        '''get all urls'''

        ses_log('[ut all_urls]', 'sending all urls')
        ses_log('[___ut session end___]', '')
        
        self.cur.execute("SELECT * FROM urls LIMIT %s" % limit)
        return str(self.cur.fetchall())

    @cherrypy.expose
    def all_owners(self, limit = 5):
        '''get all owners'''

        ses_log('[ut all_owners]', 'sending all owners')
        ses_log('[___ut session end___]', '')
        
        self.cur.execute("SELECT * FROM owners LIMIT %s" % limit)
        return str(self.cur.fetchall())

    @cherrypy.expose
    def enc(self):
        return open('/templates/enc.html')
    
    @cherrypy.expose
    def sh_log(self, limit = 100, file='log.txt'):
        '''return the shortener log'''

        ses_log('[ut sh_log]', 'sending log')
        ses_log('[___ut session end___]', '')
        
        return open(
            file,'r'  #read log file
            ).read(
                int(limit)  #read only limit chars
                ).replace(
                    '\n', '<br>'   #replace \n with <br>, because browser does not understand \n
                    )

    #@cherrypy.expose
    #def get_file(self, path):
    #    '''get any file (except files in ssl dir)'''
    #    
    #    if path.split('/')[0] != 'ssl':
    #        return open(path)
    #    else:
    #        return 'restricted'
