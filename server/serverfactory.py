'''
See LICENSE for license information.

This file contains the server's loop control. It is decoupled from
the code run within the main loop. This allows the main loop to be reloaded
and updated at runtime.
'''

##
# External modules
##

from twisted.python import log
from twisted.internet.protocol import ServerFactory
from twisted.application.service import Service

##
# Local modules
##

import serverprotocol

##
# Classes
##

class DogiFactory(ServerFactory):
    '''
    Wrapper around ServerFactory to pass a single argument to the protocol's
    init.
    '''

    def __init__(self, service, *args, **kwargs):
        self.service = service
        self.protocol = serverprotocol.DogiAdminServerProtocol
        # super()
        ServerFactory.__init__(self, *args, **kwargs)

    def buildProtocol(self, addr):
        return self.protocol(self.service)

class DogiServer(Service):

    def __init__(self, configurator):
        '''
        Initialize the Service, supplying a configurator with access to
        reliable configuration information.
        '''
        # store some arguments
        self.config = configurator

        # Create a protocol factory
        self.factory = DogiFactory(service=self)

        # prepare a mapping of clients to their connections and information
        self.whoswho = {}

        # super
        Service.__init__(self)

    def getProtocolFactory(self):
        '''
        Return the Factory which creates Protocol objects.
        '''
        return self.factory

    def registerClient(self, ident, protocol_transport, client_info):
        '''
        This is called by the underlying protocol to register a client's
        connection and information with this service. The registry is used
        to explain which clients are which when the server needs to send a
        request to a particular client.
        '''
        # Link a client to a Twisted Protocol.
        # The naming is awkward: each connected client has one protocol object.
        # Within the protocol object is the transport for data transfer.
        self.whoswho[ident] = protocol_transport
        # Cache the client's information as read from the configuration.
        self.whoswho[protocol_transport] = client_info

    def request_tunnel(self, ident, *args, **kwargs):
        '''
        Calls DogiAdminProtocol.request_tunnel() from the appropriate object
        given the ident of the target client.
        All arguments besides ident are passed through.
        '''
        return self.whoswho[ident].request_tunnel(*args, **kwargs)

    def serverStringFromConfig(self):
        # TODO this method is unused for now
        '''
        Given the configuration, generate a server string usable for Twisted
        endpoints.
        '''

        addr = self.config('get', 'server', 'address')
        port = self.config('getint', 'server', 'port')

        if addr:
            addr = ':interface={0}'.format(addr)

        cert = None
        portstring = ''
        if self.config('getboolean', 'ssl', 'enabled'):
            pem = self.config('get', 'ssl', 'certificate_pem_path')
            crt = self.config('get', 'ssl', 'certificate_path')
            key = self.config('get', 'ssl', 'certificate_key_path')
            if pem:
                # certificate_pem_path takes precedence over
                # certificate_path and certificate_key_path
                pemstring = ':certKey={0}'.format(pem)
            else:
                pemstring = ':certKey={0}:privateKey={1}'.format(crt, key)
            portstring = 'ssl:{0}{1}{2}'.format(port, address, pemstring)
        else:
            portstring = 'tcp:{0}{1}'.format(port, address)
        return portstring
