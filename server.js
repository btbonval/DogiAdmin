/***
 * Built-in modules
 ***/

var tls = require('tls');
var net = require('net');
var fs = require('fs');

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

    // listen for clients
    // track connected clients
    var clientlist = new Object();
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

        process.stdin.resume();
    
        // pipe my terminal IO through the socket's IO
        process.stdin.pipe(c);
        c.pipe(process.stdout);
    
        c.once('end', function() {
            process.stdin.unpipe(c);
            c.unpipe(process.stdout);
    
            c.end();

            // stop tracking client
            delete clientlist[clientlist[c]];
            delete clientlist[c];
    
            process.stdin.pause();
            console.log('Connection closed from ' + id.toString());
        });
    })
    server.maxConnections = 1;
    server.listen(cfg.server.port, cfg.server.address, function() {
        console.log('Listening.');
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
    clientlist[id] = socket;
    clientlist[socket] = id;
    return id;
}
