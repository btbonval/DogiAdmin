'''
See LICENSE for license information.

This file contains the server's main loop code. It is decoupled from
the code run within the main loop. This allows the main loop to be reloaded
and updated at runtime.
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

##
# Internal modules
##

from config import Configurator

class Greeting(amp.Command):
    arguments = [('iam', amp.String)]
    response = [('valid', amp.Boolean)]

class SSHToMe(amp.Command):
    arguments = [('port', amp.Integer)]
    response = [('port', amp.Integer)]

class DogiAdminServerProtocol(amp.AMP):
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

        # state machine
        self.state = 0
        # failed identification attempts
        self.failures = 0
        # TODO this should be from configuration
        self.maximum_failures = 3

    # These two functions are placeholders in case they are needed later
    def connectionMade(self):
        pass
    def connectionLost(self, reason):
        pass

    def greetz(self, ident):
        '''
        Handle the initial handshake from a client.
        '''
        # This is state == 0.
        if self.state != 0:
            # Ignore (autofail) any further requests once authorized.
            return {'valid': False}
        # Verify given identity.
        valid_client = Configurator.config('has_option', 'clients', ident)
        if valid_client: 
            # Reset failure counter
            self.failures = 0
            # Read the client's information.
            info = Configurator.config('get', 'clients', ident)
            # Register the client.
            self.service.registerClient(ident, self, info)
            self.state = 1
        else:
            self.failures = self.failures + 1
        if self.failures >= self.maximum_failures:
             # Disconnect the endpoint if it has tried too many times.
             self.transport.loseConnection()
        return {'valid': valid_client}
    Greeting.responder(greetz)

    def request_tunnel(self, port=None):
        '''
        Request the client open up a reverse SSH tunnel on local port.
        If no port is specified, one will be picked at random.
        Returns a deferred if transport.write() does?
        Definitely returns a deferred if failed.
        '''
        # This is state 1.
        if self.state != 1:
            # Raise an error if requesting a tunnel from an unauthed client.
            return defer.fail('Improper state for request.')

        if not port:
            # Autogenerate a port and hope it is free
            port = -1
            while (port < 1024):
                # Grab some random bytes
                somebytes = randbytes.insecureRandom(2)
                # Convert bytes into a number
                port = ord(somebytes[0]) << 8 + ord(somebytes[1])

        # Cache the requested port ... why not?
        self.local_ssh_port = port

        # Request client connect SSH to local system with reverse tunnel.
        # Port is to be opened on this system's end of the reverse tunnel.
        return self.callRemote(SSHToMe, port=port)
