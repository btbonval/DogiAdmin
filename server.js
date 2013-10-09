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

            // disconnect CLI socket if opened
            // stopping the server from listening via close will raise the
            // 'close' event, which is programmed to kill socket connections
            // below.
            if (clientlist.adminports[id]) clientlist.adminports[id].close();

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
        clientlist = buffer.clientlist;

        // cleanup prepended spaces
        data = data.trimLeft();
        // first word of data is client id
        client = data.split(' ', 1)[0];
        // clean up any excess whitespace at the end of command and normalize case.
        client = client.trimRight().toUpperCase();

        // check to see if the client is connected to Dogi Admin sever
        if (!clientlist.sockets[client]) {
            socket.write('No client connected with id ' + client + '.\n');
            return
        }

        // check to see if client already has a CLI socket
        if (clientlist.adminports[client]) {
            socket.write('Already listening for ' + client.toString() + ' on port ' + clientlist.adminports[client].address().port + '\n');
            return
        }

        // create new socket for the admin's CLI to the client
        clientlist.adminports[client] = net.createServer(function(c) {
            console.log('Admin connected to client ' + client + '.');

            // handle admin disconnection
            c.once('end', function() {
                // if the client disconnects, this will not be called
                if (clientlist.sockets[client]) {
                    // unhook pipes
                    clientlist.sockets[client].unpipe(c);
                    c.unpipe(clientlist.sockets[client]);
                    console.log('Client ' + client + ' disconnected.');
                }
                console.log('Admin disconnected from client ' + client + '.');
            });

            // if the admin CLI server stops listening, disconnect sockets
            clientlist.adminports[client].once('close', function() {
                if (clientlist.sockets[client]) clientlist.sockets[client].end();
                if (c) c.end();
            });

            // pipe client socket to its local socket
            // make sure the client socket doesn't get closed if the admin
            // disconnects with {'end': false}. the client socket should always
            // remain connected.
            c.pipe(clientlist.sockets[client], {'end': false});
            clientlist.sockets[client].pipe(c);
        });

        // open up new local port
        clientlist.adminports[client].maxConnections = 1;
        clientlist.adminports[client].listen(0, '127.0.0.1', function() {
            console.log('Listening for admin connection to client ' + client + ' on ' + clientlist.adminports[client].address().port);
            socket.write('Listening for admin connection to client ' + client + ' on ' + clientlist.adminports[client].address().port + '\n');
        });
    }
};
