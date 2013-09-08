'''
See LICENSE for license information.

This file contains the server's loop control. It is decoupled from
the code run within the main loop. This allows the main loop to be reloaded
and updated at runtime.
'''

##
# Built-in modules
##

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

from twisted.python import log
from twisted.python import randbytes as PRNG
from twisted.internet import defer
from twisted.internet import reactor
from twisted.application.service import Service

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
    Manage configuration IO as a caching service.
    '''

    def __init__(self, update_interval=5.0, *args, **kwargs):
        '''
        Construct the Service.
        update_interval may be set to the period between
        configuration cache updates, in seconds, as a float.
        All other parameters will be passed to the Service constructor.
        '''

        # super()
        Service.__init__(self, *args, **kwargs)

        self.configparser = None
        self.loop_timer = None
        self.update_interval = update_interval

    def _initialize_parser(self):
        # Configuration parameters.
        self.configparser = SafeConfigParser()

    def startService(self):
        '''
        Initialize the connection to the configuration store.
        '''

        # Placeholder encryption key for use when writing secure data to disk.
        self.encryption_key = None

        # Ensure the Config Parser is setup.
        self._initialize_parser()

        # Populate configuration now and "loop" it.
        self._update_config()

        # super()
        Service.startService(self)

    def stopService(self):
        '''
        Shutdown and prevent future calls to the loop.
        '''

        # super()
        Service.stopService(self)

        if self.loop_timer:
            self.loop_timer.cancel()
            self.loop_timer = None

        # TODO
        # push any pending writes out to file

    def _loop_update(self):
        '''
        Helper method to loop _update_config
        '''

        # Schedule next read prior to any execution.
        self.loop_timer = reactor.callLater(self.update_interval, self._update_config)
        
        self._update_config()

    def _update_config(self):
        '''
        Helper method to pull config into self.config.
        '''

        # TODO do we care about concurrent parser access?
        files_read = self.configparser.read(CONFIG_FILES)

        if not files_read:
            # Config reload failed.
            log.err('Config requested but unable to load. Check {0}'.format(CONFIG_FILES))

        if files_read < len(CONFIG_FILES):
            # Partial load failure, not clear how to proceed
            log.msg('Not all configuration files were loaded. Check {0}'.format(CONFIG_FILES))

    def config(self, attribute, *args, **kwargs):
        '''
        This is a front end for self.configparser that could make use of thread
        locking.
        Pass an attribute of ConfigParser (such as 'getboolean') and any
        args and kwargs that argument would take.
        '''
        retval = None
        errmsg = 'Error reading config: invalid attribute. {0} ({1}) \{{2}\}'.format(attribute, args, kwargs)

        try:
            retval = getattr(self.configparser, attribute)(*args, **kwargs)
        except AttributeError:
            log.msg(errmsg)
        return retval
