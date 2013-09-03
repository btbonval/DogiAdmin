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

import serverloop 

##
# Classes
##

class DogiServer(Service):

    def __init__(self, configurator):
        '''
        Initialize the Service, supplying a configurator with access to
        reliable configuration information.
        '''
        self.config = configurator
        self.factory = ServerFactory()
        self.factory.protocol = serverloop.DogiAdminProtocol
        # super
        Service.__init__(self)

    def getProtocolFactory(self):
        '''
        Return the Factory which creates Protocol objects.
        '''
        return self.factory

    def serverStringFromConfig(self):
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
