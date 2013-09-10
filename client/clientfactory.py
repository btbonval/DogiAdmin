'''
See LICENSE for license information.

This file contains the client's loop control.
'''

##
# External modules
##

from twisted.python import log
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.application.service import Service

##
# Local modules
##

import clientprotocol

##
# Classes
##

class DogiClient(Service):

    def __init__(self):
        '''
        Initialize the Service.
        '''
        # Create a protocol factory
        self.factory = ReconnectingClientFactory.forProtocol(clientprotocol.DogiAdminClientProtocol)

        # super
        Service.__init__(self)

    def getProtocolFactory(self):
        '''
        Return the Factory which creates Protocol objects.
        '''
        return self.factory
