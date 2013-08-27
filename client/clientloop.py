'''
See LICENSE for license information.

This file contains the server's main loop code. It is decoupled from
the code run within the main loop. This allows the main loop to be reloaded
and updated at runtime.
'''

from twisted.internet.protocol import amp

class LoopProtocol(amp.AMP):
    def connectionMade(self):
        pass
    def connectionLost(self, reason):
        pass
    def dataReceived(self, data):
        pass
