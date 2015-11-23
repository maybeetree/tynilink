import cherrypy

from funcs import *

class link:
    @cherrypy.expose
    def index(self,d=None):#geturl
        '''get long url from short or homepage'''
        url = d

        if url != None:   #if d is not specified, redirect to homepage
            ses_log('[processign url]', 'url param recieved')
            cur.execute("select longurl,pass,shorturl \
    from urls where shorturl = '%s'" % url)   #select link
            ret = cur.fetchone()
        
            if not ret:   #if link not found
                raise cherrypy.HTTPError('404')

            ses_log('[processign url]',
                        'longurl: %s, password: %s, shorturl: %s' % ret)
            #print(ret)
            
            if ret[1] == sha1('').hexdigest() or ret[1] == None:   #no password
                ses_log('[processing url]', 'link is NOT passworded')
                raise cherrypy.HTTPRedirect("/ads?destination=%s" % base64.b64encode(ret[0]))
            #this is really confusing:
            #ret[0] is the long url, and we need to encode it in base64, so
            #if the url contains params, it's not gonna mess everything up.
            #ret[2] (seen below) is the short url being passed to the
            #auth_link page. We pass the short url instead of long so the person
            #trying to acess it woudn't see
            #it in the url bar if they don't know the password. We do not need to
            #encode the short url becsue it does not contain anything dangerous.
            else:
                #sending shorturl, so longurl is not visible in url bar
                #print('hd ', ret[1])
                ses_log('[processing url]', 'link passworded')
                cherrypy.session['link_pass'] = str(ret[1])
                #cherrypy.session.acquire_lock()
                
                raise cherrypy.HTTPRedirect("/display/auth?dest=%s" % ret[2])
            #return str(ret)
            #raise cherrypy.HTTPRedirect("/ads?destination=%s" % longurl)
        else:
            #self.add_url(1,2,cur)
            ses_log('[processing url]',
                    'no url param recieved, redirecting to homepage')

            raise cherrypy.HTTPRedirect('/other/display?page=homepage')
        
    @cherrypy.expose
    def add_url(self, long, short = '', password = '', plaintext = False):
        '''the form from homepage redirects here'''

        owner_pass = cherrypy.session.get('owner_pass')
        owner = cherrypy.session.get('owner_name')
        long_enc = base64.b64encode(long)
        hashed = True
        
        if not special_match(short):   #test for invalid chars
            raise cherrypy.HTTPRedirect('static/info/invalid_chars.html')
        if not short:   #if short=None or empty str, make url to hash
            short = h6(long)
            hashed = False #if someone already shortened that url to hash
            #before, don't return "url taken"
            
        cur.execute("select shorturl from urls where shorturl = '%s'" %
                            short)

        if cur.fetchone() and hashed:   #if tuple is not empty/ url taken
            ses_log('[new_url]','url taken')
            raise cherrypy.HTTPRedirect('static/info/link/url_taken.html')
                
        cur.execute("INSERT INTO urls(shorturl,longurl,pass,owner) \
VALUES('%s','%s','%s','%s')"
                                % (short, long, sha1(password).hexdigest(), owner)) #insert link
        con.commit()
        if plaintext: return 'https://localhost?d='+short #for the tyni.link shortcut
        raise cherrypy.HTTPRedirect('other/display?page=sucsess;surl=%s;lurl=%s' % (short,long_enc))

    @cherrypy.expose
    def ads(self,destination):
        '''insert ads in here to show before redirecting to final page'''

        ses_log('[ads]', 'redirecting user')
        ses_log('[...END SESSION!!...]', '')
        
        destination = base64.b64decode(destination)#destination is encoded!
        log_visit(cherrypy.request.remote.ip, destination)

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
        cur.execute("select longurl from urls where shorturl = '%s'" % dest)
        dest2 = cur.fetchone()  #longurl
        ses_log('[auth_link]', 'got url, redirecting')
        
        raise cherrypy.HTTPRedirect("/ads?destination=%s" % base64.b64encode(dest2[0]))

