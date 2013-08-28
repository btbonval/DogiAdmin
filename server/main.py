'''
See LICENSE for license information.

This file contains the server's loop control. It is decoupled from
the code run within the main loop. This allows the main loop to be reloaded
and updated at runtime.
'''

##
# External modules
##

from twisted.internet import endpoints

##
# Built-in modules
##

from serverfactory import DogiAdminFactory
from config import Configurator

##
# if run as a script
##

if __name__ == '__main__':
    config = Configurator()
    daf = DogiAdminFactory(config)
    endpoints.serverFromString(reactor, daf.gen_server_string_from_config()).listen(daf)
    reactor.run()

##
# if run by twistd or as a module
##

else:
    application = service.Application('dogiadminserver')
    daf = DogiAdminFactory(config)
    # TODO not sure how this works with twistd?
    # https://twistedmatrix.com/documents/current/core/howto/endpoints.html
    endpoints.serverFromString(reactor, daf.gen_server_string_from_config()).listen(daf)
