import cherrypy

import  main, unstatic, funcs, links, owners, other

import os, sys

from funcs import *

'''launch all web pages'''


funcs.ses_log('\n\n[***SERVER RESTARTED!!***]', '')

print('\n\n\ndo for tracking: %s/freegeoip/freegeoip -http :8082\n\n\n' %
          os.path.dirname(os.path.abspath(__file__)))

#====cherrypy stuff====
server_config={
        'server.socket_host': '0.0.0.0',
        'server.socket_port':443,

        'server.ssl_module':'pyopenssl',
        'server.ssl_certificate':'ssl/server.crt',
        'server.ssl_private_key':'ssl/server.key',
        'tools.sessions.on' : True,
        'tools.sessions.storage_type' : "file",
        'tools.sessions.storage_path' : "session_files",
        'tools.sessions.timeout' : 180,
        #'server.ssl_certificate_chain':'gd_bundle.crt'
    }

#cherrypy.tree.mount(main.shortener(),'/',config = funcs.conf)
#cherrypy.tree.mount(ut.utils(),'/ut',config = funcs.conf_ut)
cherrypy.tree.mount(unstatic.unstatic(),'/display',config = conf)
cherrypy.tree.mount(links.link(),'/',config = conf)
cherrypy.tree.mount(owners.owner(),'/owner',config = conf)
cherrypy.tree.mount(other.main(),'/other',config = conf)

#cherrypy.config.update({'error_page.404': error_page_404})
#cherrypy.server.socket_host = socket.gethostbyname(
#    socket.gethostname()   #set tu own ip, so other computers can accsess
#    )                     #May not work on Linux

cherrypy.config.update(server_config)
cherrypy.engine.start()
cherrypy.engine.block()
#cherrypy.quickstart(shortener(), '/', conf)
