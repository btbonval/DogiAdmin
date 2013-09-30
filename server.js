/***
 * Built-in modules
 ***/

var tls = require('tls');
var net = require('net');
var fs = require('fs');
var readline = require('readline');

/***
 * Local modules
 ***/

var sslopts = require('./ssloptions');
var jsonfuncs = require('./jsonfuncs');

/***
 * Configuration
 ***/

// once config is read, remove comments, parse it, then kick off server.
fs.readFile('conf.server.json', function(err,data) {
    if (err) throw err;
    run_server(JSON.parse(jsonfuncs.remove_comments(data)));
});

/***
 * Program execution
 ***/

function run_server(cfg) {
    // Establish the sockets and main loop of the server.

    // setup some if/then stuff as dictionaries
    // TODO this executes more code than is needed. make it lazy
    var pcl = cfg.server.ssl; // true or false
    var prot = { true: tls, false: net };
    var opts = { true: sslopts.filter_options(cfg.ssl), false: {} }

    // track connected clients
    var clientlist = new Object();
    clientlist.adminports = new Object();
    clientlist.ids = new Object();
    clientlist.sockets = new Object();

    // establish administrative interface pipes
    // listen for administrator
    var admin = net.createServer(function(a) {
        // change admin interface to this connection
        console.log('Admin connected.');
        // handle admin disconnection
        a.on('end', function() {
            // unhook adminpipe
            a.unpipe();
            console.log('Admin disconnected.');
        });
        // setup a line buffer for reading commands from admin user
        buffer = readline.createInterface(a, a);
        buffer.clientlist = clientlist;
        buffer.my_socket = a;
        a.my_buffer = buffer;
        buffer.on('line', handle_protocol);
    });
    // only allow one local connection for the single administrator
    admin.maxConnections = 1;
    admin.listen(cfg.admin.port, '127.0.0.1', function() {
        console.log('Listening for admin on', cfg.admin.port);
    });

    // listen for clients
    // call the correct server listener given the configuration.
    var server = prot[pcl].createServer(opts[pcl], function(c) {
        // do not accept unauthorized connections if using TSL
        if (pcl && c.authorized === false) {
            console.log('Secure connection failed: ' + c.authorizationError);
            socket.end();
            return;
        }
        // generate client identifier and store it to the clientlist
        var id = client_id(clientlist, c);
        console.log('Connection from ' + id.toString());
        // handle client disconnection
        c.once('end', function() {
            // unhook everything
            c.unpipe();
            c.end();

            // stop tracking client
            delete clientlist.adminports[id];
            delete clientlist.sockets[id];
            delete clientlist.ids[c];

            console.log('Connection closed from ' + id.toString());
        });
    });
    server.listen(cfg.server.port, cfg.server.address, function() {
        console.log('Listening for clients.');
    });
}

// how to identify a client
function client_id(clientlist, socket) {
    // given the clientlist and socket, determine the socket's identifier and
    // associate it within the clientlist.
    // return the client identifier for good measure.

    //var iscert = socket instanceof tls.CleartextStream;
    var iscert = socket.hasOwnProperty('authorized')

    var id;
    if (iscert) {
        // TLS client identification
        // for now, it's just the certificate fingerprint
        id = socket.getPeerCertificate().fingerprint;
    } else {
        // plain text client identification
        // initialize counter if needed
        if (! clientlist.hasOwnProperty('counter') ) {
            clientlist['counter'] = 0;
        }

        // assign anonymous counter numbers for guest logins
        id = clientlist['counter'];

        // increment counter for the next login
        clientlist['counter'] = clientlist['counter'] + 1;
    }
    // cache the associated identification with the connection.
    clientlist.sockets[id] = socket;
    clientlist.ids[socket] = id;
    clientlist.adminports[id] = undefined;
    return id;
}

/***
 * Protocal Handler
 ***/

function handle_protocol(data) {
    var buffer = this;
    socket = buffer.my_socket;
    // manage client/server protocol communications.
    data = data.toString();
    // fix some kind of problem with readline or telnet in charmode
    data = data.replace('\u0000','');
    // first word of data is a command, the rest is arguments.
    var command = data.split(' ', 1)[0];
    // clean up any excess whitespace at the end of command and normalize case.
    command = command.trimRight().toUpperCase();
    // remove the command from the rest of the string
    data = data.substring(command.length);

    try {
        resolve[command](buffer, data);
    } catch (err) {
        socket.write('command(' + command + '): ' + err.toString() + '\n');
    }
}

var resolve = {
    "WHO": function(buffer, data) {
        // admin requests client info on user described in data.
        // extract single identifier from data.
        buffer.my_socket.write(Object.keys(buffer.clientlist.sockets).toString() + '\n');
    },

    "CMD": function(buffer, data) {
        // admin requests cli to the client.
        socket = buffer.my_socket;

        // TODO
        socket.write('WORK IN PROGRESS\n');
        return;

        // first word of data is client id
        client = data.split(' ', 1)[0];
        // clean up any excess whitespace at the end of command and normalize case.
        client = client.trimRight().toUpperCase();
        // return info from clientlist
        try {
            var clientsocket = buffer.clientlist[client];
        } catch (error) {
            socket.write('client was not found: ' + client.toString() + '\n');
            return
        }

        // Stop processing protocol.
        buffer.removeListener('line', handle_protocol);

        // pipe socket's IO through to admin IO
        // (don't close either client or admin pipes if the other end closes)
        socket.pipe(clientsocket);
        clientsocket.pipe(socket);
        
    }
};
