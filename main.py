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

'''these are the main pages'''

class shortener:
    def __init__(self):
        '''the cur and con objects for accsessing the db'''
        global cur, con, link_password
        
        self.cur = cur
        self.con = con

        ses_log('[init]', 'done')
        #self.link_pass=link_password
    
    @cherrypy.expose
    def index(self,d = None):
        '''redirect user to homepage or link'''

        redir = geturl(self,d)#get the url to redirect to
        
        #return 'hai'
        ses_log('\n[***SESSION STARTED!!***]', '')
        ses_log('[index]', 'redirecting user to %s' % redir)
        
        raise cherrypy.HTTPRedirect(redir)
        #raise cherrypy.HTTPError(418)

    ############FRONTEND: the pages that the user sees most of the time

    #@cherrypy.expose
    #def getuuid(self,text):
    #    return uuid(text)

    @cherrypy.expose
    def getqr(self,url):
        '''generate qr from url'''

        ses_log('[qr gen]','sending qr image')
        cherrypy.response.headers['Content-Type'] = "image/jpg"
        return new_qr(base64.b64decode(url))

    @cherrypy.expose
    def add_url(self, short, long, password = None, owner = '', owner_pass = ''):
        '''the form from homepage redirects here'''
        
        if not special_match(short):   #invalid chars
            raise cherrypy.HTTPRedirect('static/info/link/invalid_chars.html')

        long = base64.b64encode(long)
        ses_log('[add url]', 'calling func')
        result = new_url(self, short, long, password = password,
                     owner = owner, owner_pass = owner_pass)
        
        raise cherrypy.HTTPRedirect('/%s\
?lurl=%s;surl=%s;user=%s' % (result,long,short,owner))

    @cherrypy.expose
    def show_message(self, msg, redirect = False):
        '''for functions to display a message to the user.'''

        ses_log('[show message]', 'displaying message %s, redirect: %s' %
                (msg, str(redirect)))
        if redirect:
            raise cherrypy.HTTPRedirect(msg)
        return msg

    #########other
    @cherrypy.expose
    def all_owner_urls(self,owner,password):
        '''all urls of a certain owner'''

        if owner == '':   #if trying to open unregistered user
                ses_log('[all_owner_urls]', 'Trying to acsess public user!')
                return "cannot acsess uregistered user's links!!!!!"
        
        self.cur.execute("select name from owners where \
password = '%s' and name = '%s'" % (password, owner))    #Select owner name
        
        self.cur.execute("select longurl,pass,shorturl from urls where \
owner = '%s'" % cur.fetchone()[0])   #Select the links that belong to the owner

        ses_log('[all_owner_urls]', 'sending urls of owner %s, pass: %s' %
                (owner,password))

        ses_log('[...END SESSION!!...]', '')
        return str(cur.fetchall())
    
###########Backend: pages the user doesn't see a lot

    @cherrypy.expose
    def add_owner(self,name,password):
        res = new_owner(self,name,password)
        raise cherrypy.HTTPRedirect('/static/info/register/%s.html' % res)

    @cherrypy.expose
    def ads(self,destination):
        '''insert ads in here to show before redirecting to final page'''

        ses_log('[ads]', 'redirecting user')
        ses_log('[...END SESSION!!...]', '')

        print(destination[:3])

        if destination[:4] != 'http':   #if url does not include protocol, add it.
            destination = 'http://' + destination
        
        sleep(0.1)   #technical
        raise cherrypy.HTTPRedirect(destination)

    @cherrypy.expose
    def auth_link(self,dest):
        '''verify password for passworded links'''
        
        #Get longurl from shorturl
        self.cur.execute("select longurl from urls where shorturl = '%s'" % dest)
        dest2 = cur.fetchone()  #longurl
        ses_log('[auth_link]', 'got url, redirecting')
        
        raise cherrypy.HTTPRedirect("/ads?destination=%s" % dest2[0])
