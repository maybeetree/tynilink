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
from hashlib import sha1
from random_words import RandomWords


import shortener_conf as cnf

'''these are unexposed functions used by the shortener'''
'''
def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc))

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)'''

def newcaptcha(text, fontspath='captcha/fonts/'):
    cherrypy.session['capt_code'] = text
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

'''
def uuid(text):  #--------->  please ignore this function  <---------
    return base64.b64encode(  #encode into base 64
        hashlib.md5('hello')   #md5
        .digest()   #get md5
        )'''

def h6(w):  #stole this from http://www.peterbe.com/plog/best-hashing-function-in-python
    h = hashlib.md5(w)
    return h.digest().encode('base64')[:6]

    
'''
def new_owner(obj,name,password,email):
    obj.cur.execute("select name from owners where name = '%s'" %
                    name)
    if obj.cur.fetchone():   #if tuple is not empty
        ses_log('[new_owner]','owner taken')
        return 'owner_taken'
        
    obj.cur.execute("INSERT INTO owners(name,password,email) \
VALUES('%s','%s','%s')" % (name,sha1(password).hexdigest(),email))
    obj.con.commit()

    ses_log('[new owner]', 'added owner w\ name: %s, pass: %s' %
            (name,password))

    return "created_owner"
''''''
def new_qr(url):
    'generates qr code from link'

    img = qrcode.make(url)#make qr
    output = StringIO.StringIO()#create fake file(because pillow.save only writes to files)
    img.save(output)#save
    #return output
    contents = output.getvalue()#get value
    output.close()#close fake file

    ses_log('[qr creator]', 'made qr code from link %s' % url)
    return contents #return qr code image
''''''
def geturl(obj,url):
    'get long url from short or homepage'
    #link_password = obj.link_pass

    if url != None:   #if d is not specified, redirect to homepage
        ses_log('[processign url]', 'url param recieved')
        obj.cur.execute("select longurl,pass,shorturl \
from urls where shorturl = '%s'" % url)   #select link
        ret = obj.cur0.fetchone()
        
        if not ret:   #if link not found
            return '/fourofour'

        ses_log('[processign url]',
                    'longurl: %s, password: %s, shorturl: %s' % ret)
        #print(ret)
            
        if ret[1] == '' or ret[1] == None:   #no password
            ses_log('[processing url]', 'link is NOT passworded')
            return "/ads?destination=%s" % base64.b64encode(ret[0])
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
                
            return "/display/auth?dest=%s" % ret[2]
        #return str(ret)
        #raise cherrypy.HTTPRedirect("/ads?destination=%s" % longurl)
    else:
        #obj.add_url(1,2,cur)
        ses_log('[processing url]',
                'no url param recieved, redirecting to homepage')

        return '/static/homepage.html'
''''''
def new_url(obj, short, long, password = None,
            owner = '', owner_pass = ''):
    'add a new url. /add_url uses this'

    owner_pass = sha1(owner_pass).hexdigest()

    ses_log('[new_url]', 'trying to register %s as %s with password %s \
owner %s, owner pass %s' %
            (long, short, password, owner, owner_pass))
    
    if not short:   #if short=None or empty str, make url to hash
        short = h6(long)

    obj.cur.execute("select shorturl from urls where shorturl = '%s'" %
                        short)

    if obj.cur.fetchone():   #if tuple is not empty/ url taken
        ses_log('[new_url]','url taken')
        return ('static/info/link/url_taken.html', short)

    #if long[0:4] == 'http' or long[0:4] == 'https':
    #    long = long[8:]   #if link has http:// prefix, remove it
        
    if 1:    #it used to say   if owner != None:
        #here, I don't know why, so i'll just keep it like this.
        obj.cur.execute("select password from owners where name = '%s'" %
                        owner)   #get actual owner password
        actual_password = obj.cur.fetchone()

        #ses_log('[new_url]', 'user is registered')
            
        if actual_password == None:
            ses_log('[new_url]', 'Unknow user')
            return ('static/info/link/unknown_user.html', short)#if user not found
                
        if actual_password[0] == owner_pass:  #if pass correct
            ses_log('[new_url]', 'pass correct')
            obj.cur.execute("INSERT INTO urls(shorturl,longurl,pass,owner) \
VALUES('%s','%s','%s','%s')"
                                % (short, long, sha1(password).hexdigest(), owner)) #insert link
            obj.con.commit()
            return ('display/sucsess', short)
        else:
            ses_log('[new_url]', 'pass wrong')
            return ('static/info/link/wrong_password.html', short)
'''
def log_visit(ip,url,request=None):
    #return None
    info = httplib.HTTPConnection('',8082,timeout=5)
    info.connect()
    info.request('GET','/json/%s' % ip)
    #eval converts the str into a dict
    info = eval(info.getresponse().read())

    cur.execute('SELECT Id FROM urls WHERE longurl="%s"' % url)
    urlid2 = str(cur.fetchone()[0])

    #parse keys, values into strs with tuples (curly brackets)
    keys = str(['urlid']+info.keys()+['date']).replace('[', '(').replace(']', ')').replace("'",'')
    vals = str([urlid2]+info.values()+[ctime()]).replace('[', '(').replace(']', ')')

    
    cur.execute('INSERT INTO url_views %s VALUES %s' % (keys, vals))
    con.commit()

def get_login_text():
        name = cherrypy.session.get('owner_name')
        if name:
            return 'You are logged in as <b>%s </b><a href="/owner/get_all_owner_urls">account</a>' % name
        return 'You are not logged in'

            
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
'''
def validate_password(message, username, password):
    #link_password = cherrypy.session.get('link_pass')
    #cherrypy.session.release_lock()

    ses_log('[validating password]', 'password: %s entered: %s username: %s' %
          (link_password, password, username))
    #if username in USERS and USERS[username] == password:
    if password == link_password:
        ses_log('[validating password]', 'sucsess')
        return True
    ses_log('[validating password]', 'incorrect pass')
    return False
'''
'''
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
'''

conf = {
   '/': {
       'tools.staticdir.root': os.path.abspath(os.getcwd())
       },
   '/static': {
       'tools.staticdir.on': True,
       'tools.staticdir.dir': './templates/-static'
        },
   }

'''
conf_ut = {
    '/': {
       'tools.auth_basic.on': True,   #TODO: put in file!
       'tools.auth_basic.realm': 'Only developers are allowed to acsess this. \
Enter the password you see in the console',
       'tools.auth_basic.checkpassword': ut_pass_validate
    }
    }
'''

con = mdb.connect(cnf.db.host,
                  cnf.db.user,
                  base64.b64decode(cnf.db.password).decode('ascii'),
                  'shortener_urls')

cur = con.cursor()

rw = RandomWords()
