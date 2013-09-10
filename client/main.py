'''
See LICENSE for license information.

This file contains the server's loop control.
'''

# Constants define HOST/PORT location of Dogi's Admin Server
HOST = '127.0.0.1'
PORT = 3644

##
# Built-in modules
##

import sys

##
# External modules
##

try:
    from twisted.internet import service
    from twisted.application.internet import TCPClient
except ImportError:
    sys.err.println("The Twisted module must be installed and accessible.")
    sys.exit(1)

##
# Internal modules
##

from clientfactory import DogiClient

##
# Setup the service for the reactor
## 

dac = DogiClient()

application = service.Application('dogiadminclient')
TCPServer(HOST, PORT, dac.getProtocolFactory()).setServiceParent(
  service.IServiceCollection(application))

##
# TODO
# start engine if run as a script
##

#if __name__ == '__main__':
#    reactor.run()
