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
    from twisted.internet import defer
    from twisted.application.service import Service
    from twisted.python import randbytes as PRNG
except ImportError:
    sys.err.println("The Twisted module must be installed and accessible.")
    sys.exit(1)

##
# "Global" Constants
##

# one or more paths to the configuration file as used by SafeConfigParser
CONFIG_FILES = ('config.ini',)

##
# Classes
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
            files_read = self.configparser.read(CONFIG_FILES)

        if not self.running and not files_read:
            # If the loop isn't yet running and no config was read then bail
            print "No configuration found in {0}".format(CONFIG_FILES)
            sys.exit(3)

        if self.running and not files_read:
            # Server is running, but config reload failed.
            log.msg('Config requested but unable to load. Check {0}'.format(CONFIG_FILES))
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
        errmsg = 'Error reading config: invalid attribute. {0} ({1}) \{{2}\}'.format(attribute, args, kwargs)
        with self.configlock:
            try:
                retval = getattr(self.configparser, attribute)(*args, **kwargs)
            except AttributeError:
                log.msg(errmsg)
        return retval
