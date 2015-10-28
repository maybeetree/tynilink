import MySQLdb as mdb
import hashlib, base64, httplib, qrcode, StringIO
from captcha.image import ImageCaptcha
from loremipsum import get_sentences

import cherrypy
from cherrypy.lib import cptools
from cherrypy.lib import auth_basic
from cherrypy.lib.static import serve_fileobj
import socket

from time import sleep, ctime
from random import randint, choice
import sys, re, os


import shortener_conf as cnf

'''these are unexposed functions used by the shortener'''

def newcaptcha(text = 'test', fontspath='captcha/fonts/'):
    fonts = []
    for x in os.listdir(fontspath):
        if x.split('.')[-1] == 'ttf':#if font file
            fonts.append(fontspath+x)
                     
    img = StringIO.StringIO()
    
    image = ImageCaptcha(fonts=fonts)
    data = image.generate(text)
    image.write(text, img)

    contents = img.getvalue()
    img.close()

    return contents

def special_match(strg, search=re.compile(cnf.allowed_chars).search):
    return not bool(search(strg))   #test if string has invalid chars

def ses_log(func, text, logfile = 'log.txt'):
    
    text = func + ' ' + '(' + ctime() + ')' + ' ' + text + '\n'
    #Looks like this: [homepage] (Wed Sep  9 08:55:05 2015) sending homepage
    
    print(text)

    file = open(logfile, 'a')
    file.write(text)
    file.close()
    
    #with file as f: #with statement for auto-save
    #    f.write(func + ' ' + text + '\n')


def uuid(text):  #--------->  please ignore this function  <---------
    return base64.b64encode(  #encode into base 64
        hashlib.md5('hello')   #md5
        .digest()   #get md5
        )

def h6(w):  #stole this from http://www.peterbe.com/plog/best-hashing-function-in-python
    h = hashlib.md5(w)
    return h.digest().encode('base64')[:6]

def new_owner(self,name,password,email):
    self.cur.execute("select name from owners where name = '%s'" %
                    name)
    if self.cur.fetchone():   #if tuple is not empty
        ses_log('[new_owner]','owner taken')
        return 'owner_taken'
        
    self.cur.execute("INSERT INTO owners(name,password,email) \
VALUES('%s','%s','%s')" % (name,password,email))
    self.con.commit()

    ses_log('[new owner]', 'added owner w\ name: %s, pass: %s' %
            (name,password))

    return "created_owner"

def new_qr(url):
    '''generates qr code from link'''

    img = qrcode.make(url)#make qr
    output = StringIO.StringIO()#create fake file(because pillow.save only writes to files)
    img.save(output)#save
    #return output
    contents = output.getvalue()#get value
    output.close()#close fake file

    ses_log('[qr creator]', 'made qr code from link %s' % url)
    return contents #return qr code image
    
def geturl(self,url):
    '''get long url from short or homepage'''
    #link_password = self.link_pass
    global link_password

    if url != None:   #if d is not specified, redirect to homepage
        ses_log('[processign url]', 'url param recieved')
        self.cur.execute("select longurl,pass,shorturl \
from urls where shorturl = '%s'" % url)   #select link
        ret = self.cur.fetchone()
        
        if not ret:   #if link not found
            return '/fourofour'

        ses_log('[processign url]',
                    'longurl: %s, password: %s, shorturl: %s' % ret)
        #print(ret)
            
        if ret[1] == '' or ret[1] == None:   #no password
            ses_log('[processing url]', 'link is NOT passworded')
            return "/ads?destination=%s" % ret[0]#this is really confusing:
        #ret[0] is the long url, and it is already encoded in base64, becuase
        #if the url contains params, it's gonna mess everything up.
        #ret[2] (seen below) is the short url being passed to the
        #auth_link page. We pass the short url instead of long so the person
        #trying to acess it woudn't see
        #it in the url bar if they don't know the password. We do not need to
        #encode the short url becsue it does not contain anything dangerous.
        else:
            #sending shorturl, so longurl is not visible in url bar
            #print('hd ', ret[1])
            link_password = ret[1]   #for the validate_password()
            ses_log('[processing url]', 'link passworded')
            #print(ret[2])
                
            return "/auth_link?dest=%s" % ret[2]
        #return str(ret)
        #raise cherrypy.HTTPRedirect("/ads?destination=%s" % longurl)
    else:
        #self.add_url(1,2,cur)
        ses_log('[processing url]',
                'no url param recieved, redirecting to homepage')

        return '/static/homepage.html'

def new_url(self, short, long, password = None,
            owner = '', owner_pass = ''):
    '''add a new url.
/add_url uses this'''

    ses_log('[new_url]', 'trying to register %s as %s with password %s \
owner %s, owner pass %s' %
            (long, short, password, owner, owner_pass))
    
    if not short:   #if short=None or empty str, make url to hash
        short = h6(long)

    self.cur.execute("select shorturl from urls where shorturl = '%s'" %
                        short)

    if self.cur.fetchone():   #if tuple is not empty/ url taken
        ses_log('[new_url]','url taken')
        return ('static/info/link/url_taken.html', short)

    #if long[0:4] == 'http' or long[0:4] == 'https':
    #    long = long[8:]   #if link has http:// prefix, remove it
        
    if owner != None:    #if user registered
        self.cur.execute("select password from owners where name = '%s'" %
                        owner)   #get actual owner password
        actual_password = self.cur.fetchone()

        ses_log('[new_url]', 'user is registered')
            
        if actual_password == None:
            ses_log('[new_url]', 'Unknow user')
            return ('static/info/link/unknown_user.html', short)#if user not found
                
        if actual_password[0] == owner_pass:  #if pass correct
            ses_log('[new_url]', 'pass correct')
            self.cur.execute("INSERT INTO urls(shorturl,longurl,pass,owner) \
VALUES('%s','%s','%s','%s')"
                                % (short, long, password, owner)) #insert link
            self.con.commit()
            return ('display/sucsess', short)
        else:
            ses_log('[new_url]', 'pass wrong')
            return ('static/info/link/wrong_password.html', short)

def log_visit(ip,obj,url,request=None):
    info = httplib.HTTPConnection('freegeoip.net',80,timeout=0.5)
    info.connect()
    info.request('GET','/json/%s' % ip)
    #eval converts the str into a dict
    info = eval(info.getresponse().read())

    obj.cur.execute('SELECT Id FROM urls WHERE longurl="%s"' % url)
    urlid2 = str(obj.cur.fetchone()[0])

    #parse keys, values into strs with tuples (curly brackets)
    keys = str(['urlid']+info.keys()+['date']).replace('[', '(').replace(']', ')').replace("'",'')
    vals = str([urlid2]+info.values()+[ctime()]).replace('[', '(').replace(']', ')')
    
    obj.cur.execute('INSERT INTO url_views %s VALUES %s' % (keys, vals))
    obj.con.commit()

    #obj.cur.execute('SELECT * FROM url_views')
    #print(len(obj.cur.fetchall()))
            
'''def rnd_grad_f(min_color_amount=2, max_color_amount=10,
               min_r=0,min_g=0,min_b=0,
               max_r=255,max_g=255,max_b=255,
               min_percent=0,max_percent=100):
    ret_f = '#hero {'

    ret = [
'background: rgba(248,48,52,1);',
'background: -moz-linear-gradient(left, ',
'background: -webkit-gradient(left top, right top, color-stop(0%, rgba(248,48,52,1)), color-stop(27%, rgba(241,91,96,1)), color-stop(51%, rgba(246,14,25,1)), color-stop(71%, rgba(240,25,36,1)), color-stop(100%, rgba(231,39,55,1)));',
'background: -webkit-linear-gradient(left, rgba(248,48,52,1) 0%, rgba(241,91,96,1) 27%, rgba(246,14,25,1) 51%, rgba(240,25,36,1) 71%, rgba(231,39,55,1) 100%);',
'background: -o-linear-gradient(left, rgba(248,48,52,1) 0%, rgba(241,91,96,1) 27%, rgba(246,14,25,1) 51%, rgba(240,25,36,1) 71%, rgba(231,39,55,1) 100%);',
'background: -ms-linear-gradient(left, rgba(248,48,52,1) 0%, rgba(241,91,96,1) 27%, rgba(246,14,25,1) 51%, rgba(240,25,36,1) 71%, rgba(231,39,55,1) 100%);',
'background: linear-gradient(to right, rgba(248,48,52,1) 0%, rgba(241,91,96,1) 27%, rgba(246,14,25,1) 51%, rgba(240,25,36,1) 71%, rgba(231,39,55,1) 100%);'
"filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#f83034', endColorstr='#e72737', GradientType=1 );}"
]

    colors = []
    percents = []
    points = randint(min_color_amount, max_color_amount)
    insertions = [
'',
'rgba(%s1) P_S,' * points,
'',
'',
'',
'',
'',
'',
        ]

    for x in range(0,points):
        colors.append(str(
            str(randint(min_r,max_r)) + ',' +
            str(randint(min_g,max_g)) + ',' +
            str(randint(min_b,max_b)) + ','
            )
                      )

    for x in range(0,points):
        percents.append(str(
            randint(min_percent,max_percent)
            ) + '%'
                        )

    insertions[1] = insertions[1] % tuple(colors)
    insertions[1] = insertions[1].replace('P_S','%s')
    insertions[1] = insertions[1] % tuple(percents)

    

    for x in range(0,len(ret)):
        ret[x] += insertions[x]
        
    
    return str(ret[0])

'''
def validate_password(message, username, password):
    global link_password

    ses_log('[validating password]', 'password: %s entered: %s username: %s' %
          (link_password, password, username))
    #if username in USERS and USERS[username] == password:
    if password == link_password:
        ses_log('[validating password]', 'sucsess')
        return True
    ses_log('[validating password]', 'incorrect pass')
    return False

def ut_pass_validate(message, username, password):
    ses_log('[ut acsess]', 'func not done yet! returning True')
    return True
#    ses_log('[ut pass checker]', 'begin')
#    
#    real_pass = chr(randint(33,126)) * randint(1,5)
#    ses_log('[ut pass checker]', 'password: %s' % real_pass)
#    if password == real_pass:
#        ses_log('[ut pass checker]', 'pass sucsessfull')
#        ses_log('[ut pass checker]', 'end')
#        return True
#    ses_log('[ut pass checker]', 'pass UNsucsessfull')
#    ses_log('[ut pass checker]', 'end')
#    return False

conf = {
   '/': {
       'tools.staticdir.root': os.path.abspath(os.getcwd())
       },
   '/static': {
       'tools.staticdir.on': True,
       'tools.staticdir.dir': './templates'
        },
   '/auth_link': {
       'tools.auth_basic.on': True,   #TODO: put in file!
       'tools.auth_basic.realm': 'This link requires a password.',
       'tools.auth_basic.checkpassword': validate_password
    }
   }

conf_ut = {
    '/': {
       'tools.auth_basic.on': True,   #TODO: put in file!
       'tools.auth_basic.realm': 'Only developers are allowed to acsess this. \
Enter the password you see in the console',
       'tools.auth_basic.checkpassword': ut_pass_validate
    }
    }

con = mdb.connect(cnf.db.host,
                  cnf.db.user,
                  base64.b64decode(cnf.db.password).decode('ascii'),
                  'shortener_urls')
cur = con.cursor()

link_password = None   #for validate_password()

capt_code = '' #for captcha
