/***
 * Built-in modules
 ***/

var tls = require('tls');
var net = require('net');
var fs = require('fs');
var spawn = require('child_process').spawn

/***
 * External modules
 ***/

var pty = require('pty.js');

/***
 * Local modules
 ***/

var sslopts = require('./ssloptions');
var jsonfuncs = require('./jsonfuncs');

/***
 * Configuration
 **/

// once config is read, remove comments, parse it, then kick off server.
fs.readFile('conf.client.json', function(err,data) {
    if (err) throw err;
    run_client(JSON.parse(jsonfuncs.remove_comments(data)));
});

/***
 * Program execution
 ***/

function run_client(cfg) {
    // Establish the sockets and main loop of the client.

    // setup some if/then stuff as dictionaries
    // TODO this executes more code than is needed. make it lazy
    var pcl = cfg.remote.ssl; // true or false
    var prot = { true: tls, false: net };
    var opts = { true: sslopts.filter_options(cfg.ssl), false: {} }

    // update the options to contain host and port
    opts[pcl].host = cfg.remote.address;
    opts[pcl].port = cfg.remote.port;

    // connect the socket.
    var socket = prot[pcl].connect(opts[pcl], function() {
        // check to see if secure connection failed.
        if (pcl && socket.authorized === false) {
            console.log('Secure connection failed: ' + socket.authorizationError);
            socket.end();
        } else {
            console.log('Connected!');
            // begin handling protocol
            socket.on('data', handle_protocol);
        }
    });
}

/***
 * Protocol Handler
 ***/

function handle_protocol(data) {
    var socket = this;
    // manage client/server protocol communications.
    data = data.toString();
    // first word of data is a command, the rest is arguments.
    var command = data.split(' ', 1)[0];
    // clean up any excess whitespace at the end of command and normalize case.
    command = command.trimRight().toUpperCase();
    // remove the command from the rest of the string
    data = data.substring(command.length);

    resolve[command](socket, data);
}

var resolve = {
    "PING": function(socket, args) {
        // Server sent PING commmand.
        // Respond with PONG.
        socket.write('PONG\n');
    },

    "MAC": function(socket, args) {
        // Server sent the MAC command.
        // Respond with the MAC address of the connected socket.
        // Unfortunately node.js does not support MAC address retrieval
        // natively, so this will be captured through bash.

        // Connected socket local IP address.
        var localIP = socket.address().address;
        // Grab the hardware address from ifconfig for the given IP address.
        // Assumes Linux base system, but so does 'bash' below.
        console.log('ip',localIP.toString());
        subproc = spawn('bash', ['-c','ifconfig | grep -B1 ' + localIP.toString()]);
        subproc.stdout.on('data', function(data) {
            data = data.toString();
            // Extract MAC from ifconfig and send it to server.
            // Assumes IPv4 for now ('HWaddr ##:##:##:##:##:##')
            var start = data.search('HWaddr ') + 7;
            // not found is -1, -1 + 7 = 6
            if (start == 6) {
                socket.write('ERR No HWaddr found, IP address: ' +
                             localIP.toString() + '\n');
                return;
            }
            var end = start + 17;
            socket.write(data.slice(start, end));
            socket.write('\n');
        });
        subproc.stderr.on('data', function(data) {
            socket.write('ERROR' + data.toString() + '\n');
        });
    },

    "BYE": function(socket, args) {
        // Server sent BYE command.
        // Close socket.
        console.log('Server requests a disconnect. Complying with request...');
        socket.end();
    },

    "TTY": function(socket, args) {
        // Server sent "TTY" command.
        // Crack open a shell.
        console.log('Server requests a TTY.');
        var tty = new pty.Terminal('bash', [], {
            name: 'xterm-color',
            cols: 80,
            rows: 30,
            cwd: process.env.HOME,
            env: process.env
        });
        // Stop processing protocol.
        socket.removeListener('data', handle_protocol);
        // Connect the shell and socket together.
        tty.pipe(socket); // bash.stdout | clientsocket.write
        socket.pipe(tty); // clientsocket.read | bash.stdin
        console.log('Terminal established.');

        // Disconnect pipes when appropriate.
        events = ['end','timeout','close','destroy','unpipe'];
        var reset = function() {
            console.log('Terminal reset indicated.');
            // Turn off reset listeners, they won't be needed now.
            for(var i = 0; i < events.length; i++) {
                the_event = events[i];
                tty.removeListener(the_event, reset);
                socket.removeListener(the_event, reset);
            }
            // Disconnect shell from socket. (maybe this is redundant?)
            tty.socket.unpipe(socket);
            socket.unpipe(tty);
            // Object cleanup.
            delete tty;
            // Start processing protocol again.
            socket.on('data', handle_protocol);
            console.log('Terminal reset completed.');
        }
        for(var i = 0; i < events.length; i++) {
            the_event = events[i];
            tty.on(the_event, reset);
            socket.on(the_event, reset);
        }
    }
}
