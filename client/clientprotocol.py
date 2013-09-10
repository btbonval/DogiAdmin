'''
See LICENSE for license information.

This file contains the client's main loop code.
'''

##
# Built-in modules
##

from twisted.python import randbytes

##
# External modules
##

from twisted.internet import defer
from twisted.internet.protocol import amp

class Greeting(amp.Command):
    arguments = [('iam', amp.String)]
    response = [('valid', amp.Boolean)]

class SSHToMe(amp.Command):
    arguments = [('port', amp.Integer)]
    response = [('port', amp.Integer)]

class DogiAdminClientProtocol(amp.AMP):
    '''
    Server side of the Dogi Administration protocol.
    '''

    def __init__(self, service, *args, **kwargs):
        '''
        Initialize a registry of connections.
        '''
        # super()
        amp.AMP.__init__(self, *args, **kwargs)

        # for parent callbacks
        self.service = service

    def connectionMade(self):
        '''
        Once a connection is established, send my ident to the server.
        '''
        # TODO come up with a way to determine ident for the client?
        d = self.callRemote(Greeting, iam='TylerDurden')
        # TODO d.errBack()
 
    # Placeholder in case needed later
    def connectionLost(self, reason):
        pass

    def SSH_to_me(self, port):
        '''
        Requested to SSH to the admin server!
        '''
        # TODO shell exec reverse SSH tunnel to server
        pass
    SSHToMe.responder(SSH_to_me)
