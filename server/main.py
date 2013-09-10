'''
See LICENSE for license information.

This file contains the server's loop control.
'''

##
# Built-in modules
##

import sys

##
# External modules
##

try:
    from twisted.internet import service
    from twisted.application.internet import TCPServer
except ImportError:
    sys.err.println("The Twisted module must be installed and accessible.")
    sys.exit(1)

##
# Internal modules
##

from serverfactory import DogiServer
from config import Configurator

##
# Setup the service for the reactor
## 

config = Configurator()
das = DogiServer(config)

application = service.Application('dogiadminserver')
TCPServer(3644, das.getProtocolFactory()).setServiceParent(
  service.IServiceCollection(application))

##
# TODO
# start engine if run as a script
##

#if __name__ == '__main__':
#    reactor.run()
