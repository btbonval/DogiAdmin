'''
See LICENSE for license information.

This file contains the server's main loop code. It is decoupled from
the code run within the main loop. This allows the main loop to be reloaded
and updated at runtime.
'''

from twisted.internet.protocol import amp

class Greeting(amp.Command):
    arguments = [('iam', amp.String)]
    response = [('valid', amp.Boolean)]

class LoopProtocol(amp.AMP):
    def connectionMade(self):
        pass
    def connectionLost(self, reason):
        pass
    def dataReceived(self, data):
        pass

    def resolve_id(self, identity):
        # Get an id from the client and verify it is valid.
        # TODO
        return 0
