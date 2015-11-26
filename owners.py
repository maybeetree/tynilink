import cherrypy

from funcs import *

class owner:
    @cherrypy.expose
    def login(self,name='',password='',redir='/owner/get_all_owner_urls'):#Store password and login for user
        password = sha1(password).hexdigest()
        cur.execute("select password from owners where name = '%s'" % name)
        actual_pass = cur.fetchone()

        if not special_match(name) or not special_match(password):
            raise cherrypy.HTTPRedirect('static/info/invalid_chars.html')
        if actual_pass:#if found actuall pass
            if password == actual_pass[0]:
                cur.execute("select perm from owners where name = '%s'" % name)
                cherrypy.session['owner_pass'] = password
                cherrypy.session['owner_name'] = name
                cherrypy.session['owner_permission'] = str(cur.fetchone()[0])
                raise cherrypy.HTTPRedirect(redir)
            else:
                return 'incorrect pass'
        else:
            return 'unkown owner'
        
    @cherrypy.expose
    def get_all_owner_urls(self):#get all urls of owner (login+pass stored in session)
        '''all urls of a certain owner'''
        #password = cherrypy.session.get('owner_pass')
        owner = cherrypy.session.get('owner_name')
        if not owner:
            return 'permission denied'
                
        cur.execute("select * from urls where \
owner = '%s'" % owner)   #Select the links that belong to the owner

        ses_log('[all_owner_urls]', 'sending urls of owner %s' %
                (owner))

        ses_log('[...END SESSION!!...]', '')
        return str(cur.fetchall())
    
    @cherrypy.expose
    def new_owner(self,name,password,email,captcha):
        if not special_match(name) or not special_match(password):
            raise cherrypy.HTTPRedirect('static/info/invalid_chars.html')
        
        #if cpatcha incorrect
        if captcha != cherrypy.session.get('capt_code'):
            return 'captcha incorrect'
        
        cur.execute("select name from owners where name = '%s'" %
                    name)
        if cur.fetchone():   #if tuple is not empty
            ses_log('[new_owner]','owner taken')
            return 'owner_taken'
        
        cur.execute("INSERT INTO owners(name,password,email,perm) \
VALUES('%s','%s','%s',1)" % (name,sha1(password).hexdigest(),email))
        con.commit()

        ses_log('[new owner]', 'added owner w\ name: %s, pass: %s' %
                (name,password))

        return "created_owner"
