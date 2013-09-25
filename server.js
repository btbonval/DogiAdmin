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
    var pcl = cfg.server.ssl; // true or false
    var prot = { true: tls, false: net };
    var opts = { true: sslopts.filter_options(cfg.ssl), false: {} }

    console.log(opts);

    // call the correct server listener given the configuration.
    var server = prot[pcl].createServer(opts[pcl], function(c) {
        console.log('Connection!');
        process.stdin.resume();
    
        // pipe my terminal IO through the socket's IO
        process.stdin.pipe(c);
        c.pipe(process.stdout);
    
        c.once('end', function() {
            process.stdin.unpipe(c);
            c.unpipe(process.stdout);
    
            c.end();
    
            process.stdin.pause();
            console.log('Connection closed.');
        });
    })
    server.maxConnections = 1;
    server.listen(cfg.server.port, cfg.server.address, function() {
        console.log('Listening.');
    });
}
