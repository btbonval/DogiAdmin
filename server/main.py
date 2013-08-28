'''
See LICENSE for license information.

This file contains the server's loop control. It is decoupled from
the code run within the main loop. This allows the main loop to be reloaded
and updated at runtime.
'''

##
# Built-in modules
##

import sys
import platform.python_version as py_version
from threading import RLock

if py_version.startswith('2.'):
    # Support Python 2.x
    from ConfigParser import SafeConfigParser
elif py_version.startswith('3.'):
    # Support Python 3.x
    from configparser import SafeConfigParser

##
# External modules
##

try:
    from twisted.python import log
    from twisted.internet import ssl
    from twisted.internet import reactor
    from twisted.internet import endpoints
    from twisted.internet.protocol import ServerFactory
except ImportError:
    sys.err.println("The Twisted module must be installed and accessible.")
    sys.exit(1)

##
# Local modules
##

import config
import serverloop 

##
# Classes
##

class DogiServerFactory(ServerFactory):
    protocol = serverloop.LoopProtocol

    def gen_server_string(self):
        addr = self.config('get', 'server', 'address')
        port = self.config('getint', 'server', 'port')
        factory = Factory()
        factory.protocol = serverloop.LoopProtocol
     
        cert = None
        portstring = ''
        if self.config('getboolean', 'ssl', 'enabled'):
            # https://twistedmatrix.com/documents/current/core/howto/ssl.html
            pem = self.config('get', 'ssl', 'certificate_pem_path')
            crt = self.config('get', 'ssl', 'certificate_path')
            key = self.config('get', 'ssl', 'certificate_key_path')
            if pem:
                # PEM overrides the other two options.
                # Locate key and certificate in a single file.
                with open(pem) as pemdata:
                    cert = ssl.PrivateCertificate.loadPEM(pemdata.read())
            else:
                # Locate key and certificate separately.
                with open(key) as keydata:
                    with open(crt) as crtdata:
                        cert = ssl.PrivateCertificate.loadPEM(
                          keydata.read() + crtdata.read()) 
            portstring = 'ssl:{0}'.format(port)
            reactor.listenSSL(port, factory, cert.options())
        else:
            portstring = 'tcp:{0}'.format(port)
            reactor.listenTCP(port, factory)
        return portstring

        # TODO
        # endpoints.serverFromString(reactor, portstring).listen(factory)
 

if __name__ == '__main__':
    start_app()
