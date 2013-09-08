'''
See LICENSE for license information.

This file contains the server's main loop code. It is decoupled from
the code run within the main loop. This allows the main loop to be reloaded
and updated at runtime.
'''

##
# External modules
##

from twisted.internet.protocol import amp

##
# Internal modules
##

from config import Configurator

class Greeting(amp.Command):
    arguments = [('iam', amp.String)]
    response = [('valid', amp.Boolean)]

class DogiAdminProtocol(amp.AMP):
    '''
    Server which responds to commands.
    '''

    def __init__(self, *args, **kwargs):
        '''
        Initialize a registry of connections.
        '''
        # super()
        amp.AMP.__init__(self, *args, **kwargs)

        self.whoswho = {}

    # These two functions are placeholders in case they are needed later
    def connectionMade(self):
        pass
    def connectionLost(self, reason):
        pass

    def greetz(self, ident):
        '''
        Handle the initial handshake from a client.
        '''
        # Verify given identity.
        valid_client = Configurator.config('has_option', 'clients', ident)
        # TODO how to find the remote cnxn handle?
        return {'valid': valid_client}
    Greeting.responder(greetz)

    def _request_tunnel(self, port):

    def request_tunnel(self, ident, port=None):
        '''
        Request the client (ident) open up a reverse SSH tunnel on local port.
        If no port is specified, one will be picked at random.
        '''
        destination = self.whoswho[ident]
        # TODO this won't work, the connection is already established.
        cnxnDeferred = connectProtocol(destination, AMP())
        # once connection is established, request a tunnel
        cnxnDeferred.addCallback(self._request_tunnel, port)
