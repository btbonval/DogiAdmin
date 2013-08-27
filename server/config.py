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
from threading import RLock

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
    from twisted.application.service import Service
except ImportError:
    sys.err.println("The Twisted module must be installed and accessible.")
    sys.exit(1)

try:
    # A cryptographically secure P-RNG is needed for temporary keys.
    import OpenSSL.rand as PRNG
except ImportError:
    sys.err.println("The OpenSSL module must be installed and accessible.")
    sys.exit(2)

##
# "Global" Constants
##

# one or more paths to the configuration file as used by SafeConfigParser
config_files = ('config.ini',)

##
# Main Loop class definition
##

class Configurator(Service):
    '''
    Manage configuration IO as a service.
    '''

    def startService(self):
        '''
        Initialize the connection to the configuration store.
        '''

        # super()
        Service.startService(self)

        # Configuration parameters.
        self.configparser = SafeConfigParser()
        self.configlock = RLock()

        # Populate configuration now or die trying.
        self.update_config()
        # Timed updates to be called.

        # Placeholder encryption key for use when writing secure data to disk.
        self.encryption_key = None

    def update_config(self):
        '''
        Helper method to pull config into self.config.
        '''
        # Make sure self.configparser is not being used concurrently.
        with self.configlock:
            files_read = self.configparser.read(config_files)

        if not self.running and not files_read:
            # If the loop isn't yet running and no config was read then bail
            print "No configuration found in {0}".format(config_files)
            sys.exit(3)

        if self.running and not files_read:
            # Server is running, but config reload failed.
            log.msg('Config requested but unable to load. Check {0}'.format(config_files))
            return 'poop'

        # At this point, files_read is not empty, so config was read.
        # Hooray!

    def config(self, attribute, *args, **kwargs):
        '''
        This is a front end for self.configparser that makes use of thread
        locking.
        Pass an attribute of ConfigParser (such as 'getboolean') and any
        args and kwargs that argument would take.
        '''
        retval = None
        with self.configlock:
            try:
                retval = getattr(self.configparser, attribute)(*args, **kwargs)
            except AttributeError:
                log.msg('Error reading config: invalid attribute. {0} ({1}) \{{2}\}'.format(attribute, args, kwargs))
        return retval

    def run(self):
        '''
        Begin running the self.serverloop protocol in a twisted reactor.
        '''
        if self.running:
            raise RuntimeException('Server loop controller appears to be running already.')
        else:
            addr = self.config('get', 'server', 'address')
            port = self.config('getint', 'server', 'port')
            factory = Factory()
            # TODO the reload() might need to go into the Protocol...
            reload(self.serverloop)
            factory.protocol = self.serverloop.LoopProtocol

            cert = None
            if self.config('getboolean', 'ssl', 'enabled'):
                # https://twistedmatrix.com/documents/current/core/howto/ssl.html
                pem = self.config('get', 'ssl', 'certificate_pem_path')
                crt = self.config('get', 'ssl', 'certificate_path')
                key = self.config('get', 'ssl', 'certificate_key_path')
                if pem:
                    # PEM overrides the other two options.
                    # Locate key and certificate in a single file.
                    with open(pem) as pemdata:
                        cert = ssl.PrivateCertificate.loadPEM(pemdata.read())
                else:
                    # Locate key and certificate separately.
                    with open(key) as keydata:
                        with open(crt) as crtdata:
                            cert = ssl.PrivateCertificate.loadPEM(
                              keydata.read() + crtdata.read()) 
                reactor.listenSSL(port, factory, cert.options())
            else:
                reactor.listenTCP(port, factory)


if __name__ == '__main__':
    engine = LoopEngine()
    engine.run()
