import cherrypy

from funcs import *

class main:
    @cherrypy.expose
    def index(self,d = None):
        return 'hi'

    @cherrypy.expose
    def getqr(self,url):
        '''generates qr code from link'''
        cherrypy.response.headers['Content-Type'] = "image/jpg"

        url = base64.b64decode(url)
        img = qrcode.make(url)#make qr
        output = StringIO.StringIO()#create fake file(because pillow.save only writes to files)
        img.save(output)#save
        #return output
        contents = output.getvalue()#get value
        output.close()#close fake file

        ses_log('[qr creator]', 'made qr code from link %s' % url)
        return contents #return qr code image

    @cherrypy.expose
    def getcaptcha(self,fontspath='captcha/fonts/'):
        cherrypy.response.headers['Content-Type'] = "image/png"

        text = rw.random_word()
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

    @cherrypy.expose
    def exec_mysql(self,command):
        if cherrypy.session.get('owner_permission') >= 2:
            cur.execute(command)
            return str(cur.fetchall())
        return 'access denied'

    @cherrypy.expose
    def display(self,page,template='templates/tynilink_template.html',**kwargs):
        mainpage = open(template).read()
        replace = (
            open('templates/%s/style_links.html'%page).read(),
            open('templates/%s/script_links.html'%page).read(),
            open('templates/%s/header.html'%page).read(),
            open('templates/%s/message.html'%page).read(),
            get_login_text(),
            open('templates/%s/content.html'%page).read()
            )

        mainpage = mainpage % replace
        mainpage = mainpage % tuple(kwargs.values())

        return mainpage
            
