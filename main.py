import MySQLdb as mdb
import StringIO
import qrcode
import hashlib, base64
from random_words import RandomWords

import cherrypy
from cherrypy.lib import cptools
from cherrypy.lib import auth_basic
from cherrypy.lib.static import serve_fileobj
import socket

import os
from time import sleep, ctime
from random import randint
import sys
from hashlib import sha1

from funcs import *

'''these are the main pages'''

class shortener:
    def __init__(self):
        '''the cur and con objects for accsessing the db'''
        global cur,con
        
        self.cur = cur
        self.con = con
        #self.capt_code = capt_code
        self.rw = RandomWords()
        self.pass_enc = self.rw.random_word()

        ses_log('[init]', 'done')
        #self.link_pass=link_password
    
    @cherrypy.expose
    def index(self,d = None):
        '''redirect user to homepage or link'''

        #capt_code = get_sentences(1)
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
    def getcaptcha(self):
        cherrypy.response.headers['Content-Type'] = "image/png"
        #self.capt_code = self.rw.random_word()
        return newcaptcha(self.rw.random_word())

    @cherrypy.expose
    def getqr(self,url):
        '''generate qr from url'''

        ses_log('[qr gen]','sending qr image')
        cherrypy.response.headers['Content-Type'] = "image/jpg"
        return new_qr(base64.b64decode(url))

    @cherrypy.expose
    def add_url(self, short, long, password = None, owner = '', owner_pass = ''):
        '''the form from homepage redirects here'''
        #this gets called by the form, so the dangerous chars in the url are escaped
        
        if not special_match(short):   #test for invalid chars
            raise cherrypy.HTTPRedirect('static/info/invalid_chars.html')
        
        #long = base64.b64decode(long)
        ses_log('[add url]', 'calling func')
        result = new_url(self, short, long, password = password,
                     owner = owner, owner_pass = owner_pass)
        
        raise cherrypy.HTTPRedirect('/%s\
?surl=%s;lurl=%s' % (result[0],result[1],base64.b64encode(long)))
    #using result[1] instead of short, because if short is empty,
    #the function will set it to the hash of long, but
    #the short in this func won't be changed

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
    def login(self,name,password):#Store password and login for user
        password = sha1(password).hexdigest()
        self.cur0.execute("select password from owners where name = '%s'" % name)
        actual_pass = self.cur.fetchone()

        if name:
            if actual_pass:
                if password == actual_pass[0]:
                   self.cur.execute("select perm from owners where name = '%s'" % name)
                   cherrypy.session['owner_pass'] = password
                   cherrypy.session['owner_name'] = name
                   cherrypy.session['owner_permission'] = str(self.cur.fetchone()[0])
                else:
                    return 'incorrect pass'
            else:
                return 'unkown owner'
        else:
            return 'permission denied'
        
        raise cherrypy.HTTPRedirect('/get_all_owner_urls')

    @cherrypy.expose
    def exec_mysql(self,comman=''):
        perm_lvl = cherrypy.session.get('owner_permission')
        #self.cur.execute(command)
        return str(perm_lvl)

        #return str(self.cur.fetchall())
        
    @cherrypy.expose
    def get_all_owner_urls(self):#get all urls of owner (login+pass stored in session)
        '''all urls of a certain owner'''
        password = cherrypy.session.get('owner_pass')
        owner = cherrypy.session.get('owner_name')
                
        self.cur.execute("select longurl,pass,shorturl from urls where \
owner = '%s'" % owner[0])   #Select the links that belong to the owner

        ses_log('[all_owner_urls]', 'sending urls of owner %s, pass: %s' %
                (owner,password))

        ses_log('[...END SESSION!!...]', '')
        return str(cur.fetchall())
    
###########Backend: pages the user doesn't see a lot

    @cherrypy.expose
    def add_owner(self,name,password,email,captcha):
        #if invalid chars used
        if not special_match(name) or not special_match(password):
            raise cherrypy.HTTPRedirect('static/info/invalid_chars.html')
        #if cpatcha incorrect
        if captcha != cherrypy.session.get('capt_code'):
            return 'captcha incorrect'
    
        res = new_owner(self,name,password,email)
        return res
        #raise cherrypy.HTTPRedirect('/static/info/register/%s.html' % res)

    @cherrypy.expose
    def ads(self,destination):
        '''insert ads in here to show before redirecting to final page'''

        ses_log('[ads]', 'redirecting user')
        ses_log('[...END SESSION!!...]', '')
        
        destination = base64.b64decode(destination)#destination is encoded!
        log_visit(cherrypy.request.remote.ip, self, destination)

        if destination[:4] != 'http':   #if url does not include protocol, add it.
            destination = 'http://' + destination
        
        sleep(0.1)   #technical
        raise cherrypy.HTTPRedirect(destination.decode('ascii'))

    @cherrypy.expose
    def auth_link(self,dest,password):
        '''verify password for passworded links'''
        
        password = sha1(password).hexdigest()
        link_password = cherrypy.session.get('link_pass')
        ses_log('[validating password]', 'password: %s entered: %s' %
          (link_password, password))
        if password == link_password:
            ses_log('[validating password]', 'sucsess')
        else: return 'Pass incorrect'
        
        #Get longurl from shorturl
        self.cur.execute("select longurl from urls where shorturl = '%s'" % dest)
        dest2 = cur.fetchone()  #longurl
        ses_log('[auth_link]', 'got url, redirecting')
        
        raise cherrypy.HTTPRedirect("/ads?destination=%s" % base64.b64encode(dest2[0]))
