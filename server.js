//var tls = require('tls');
var tls = require('net');
var net = require('net');

var server = tls.createServer({}, function(c) {
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
server.listen(8064, function() {
    console.log('Listening.');
});
