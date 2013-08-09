'''
See LICENSE for license information.

This file contains the server's main loop code. It is decoupled from
the code run within the main loop. This allows the main loop to be reloaded
and updated at runtime.
'''

from twisted.internet.protocol import Protocol

class LoopProtocol(Protocol):
    def connectionMade(self):
        self.transport.write('BYE!')
        self.transport.loseConnection()
