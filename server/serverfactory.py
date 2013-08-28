'''
See LICENSE for license information.

This file contains the server's loop control. It is decoupled from
the code run within the main loop. This allows the main loop to be reloaded
and updated at runtime.
'''

##
# Built-in modules
##

import sys
import platform.python_version as py_version

if py_version.startswith('2.'):
    # Support Python 2.x
    from ConfigParser import SafeConfigParser
elif py_version.startswith('3.'):
    # Support Python 3.x
    from configparser import SafeConfigParser

##
# External modules
##

try:
    from twisted.python import log
    from twisted.internet import reactor
    from twisted.internet import endpoints
    from twisted.internet.protocol import ServerFactory
except ImportError:
    sys.err.println("The Twisted module must be installed and accessible.")
    sys.exit(1)

##
# Local modules
##

import config
import serverloop 

##
# Classes
##

class DogiServerFactory(ServerFactory):
    protocol = serverloop.DogiAdminProtocol

    def __init__(self, configurator):
        self.config = configurator

    def gen_server_string_from_config(self):
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
