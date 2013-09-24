/***
 * Built-in modules
 ***/

//var tls = require('tls');
var tls = require('net');

/***
 * External modules
 ***/

var pty = require('pty.js');

/***
 * Initialize client socket handling.
 ***/

var socket = tls.connect(8064, 'localhost');
var tty = null;

/***
 * Protocol Handler
 ***/

socket.on('data', handle_protocol);

function handle_protocol(data) {
    // manage client/server protocol communications.
    data = data.toString();
    // first word of data is a command, the rest is arguments.
    var command = data.split(' ', 1)[0];
    // clean up any excess whitespace at the end of command and normalize case.
    command = command.trimRight().toUpperCase();
    // remove the command from the rest of the string
    data = data.substring(command.length);

    resolve[command](data);
}

var resolve = {
    "HANDSHAKE": function(args) {
        // Server sent HANDSHAKE command.
        // Return client identifier.
        // TODO
    },

    "PING": function(args) {
        // Server sent PING commmand.
        // Respond with PONG.
        socket.write('PONG\n');
    },

    "BYE": function(args) {
        // Server sent BYE command.
        // Close socket.
        console.log('Server requests a disconnect. Complying with request...');
        socket.end();
    },

    "TTY": function(args) {
        // Server sent "TTY" command.
        // Crack open a shell.
        console.log('Server requests a TTY.');
        tty = new pty.Terminal('bash', [], {
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
