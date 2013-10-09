# DogiAdmin

## License
This software is released under the MIT License. See LICENSE.

## Security
*NOTICE!* This software is meant to be used with an x509 authentication
framework. Included are some examples for setting up such a framework, but
this is just for demonstration purposes! Do not rely on the examples!

The administrator will generate one x509 Certificate Authority (CA) and at least
one x509 certificate. The first certificate, signed by the CA, will be used for
the server. Each client will then need his or her own unique certificate,
signed by the CA. Each client will also need the CA public certificate to
verify the server.

The server's certificate should include the FQDN that the server will be
reached at either as the CN or as part of v3 extension subjectAlternativeName.
Included examples show how to make use of SAN, in which case CN is not used.

I'm presently unclear if the client's certificate needs to have a valid CN
or SAN section. This should be tested.

When the client connects to the server, assuming both are configured for TSL,
then the certificates will be compared against the CA for validity. If the
client's certificate is not signed by your CA, he or she will be disconnected.
If the server's certificate is not signed by your CA (for example, during a
masquerade attack), the client will disconnect. If client and server both
validate each other, then the TLS connection will be established.

*NOTICE!* You may disable TLS in the server and client configuration. Doing so
would be insecure, but it might be useful for troubleshooting or development.

## Server

### Configuration
The server's configuration is contained in `conf.server.json`. This file uses
the JSON format, which is actually quite onerous for people to use. There is
an example configuration in the repository named `conf.server.json.example`.

Proper JSON does not allow comments. I wrote a filter which removes comments
from the JSON prior to parsing it, because comments are useful, and JSON is not.

#### server section
Example:
``` JSON
{
"admin": {
    "port": 11123
},

"server": {
    "address": "127.0.0.1",
    "port": 8064,
    "ssl": true
}
}
```

* admin
 * `port` is a 2-byte integer. 0-1023 usually require advanced privileges.
Connect to this port on the localhost to access the administrative interface.
* server
 * `address` follows usual `bind(2)` rules. It should be a string. If you
aren't using Unix, I don't know what to tell you about this.
 * `port` is a 2-byte integer. 0-1023 usually require advanced privileges.
 * `ssl` should always be true! See Security above.

#### TSL section
This example shows the usual style of supplying PEM files.
``` JSON
{
"ssl": {
    "keyfile": "test/x509/certs/CERT1A.rsa",
    "certfile": "test/x509/certs/CERT1A.crt",
    "cafile": "test/x509/certs/CA1.crt",

    "requestCert": true,
    "rejectUnauthorized": true
}
}
```

This example shows the unusual style (used by node.js tls module) of supplying
PEM data.
``` JSON
{
"ssl": {
    "key": "DATA",
    "cert": "DATA",
    "ca": "DATA",

    "requestCert": true,
    "rejectUnauthorized": true

}
}
```

* `requestCert` requires the connecting client to provide an x509 certificate.
* `rejectUnauthorized` rejects clients that send an invalid x509 certificate.
* `ca` or `cafile` is your Certificate Authority PEM data (or path to file).
* `cert` or `certfile` is the server's certificate PEM data (or path to file).
* `key` or `keyfile` is the server's RSA key data (or path to file).

`ca` and `cafile` are mutually exclusive. Supply one or the other, but not
both. The same is true for `cert` and `certfile` as well as `key` and `keyfile`.
`ca` and `certfile` may be specified, so long as `cafile` and `cert` do not
appear. The same applies with the other combinations.

### Execution
Run the server with `node server.js`.

Once the server is running, connect to the admin interace with
`telnet localhost 11123`. This assumes port 11123 is set for the admin
interface (see server configuration above). Replace 11123 with the appropriate
port based on the configuration setting.

### Admin Interface Commands

* `WHO` will list connected clients by their unique ID.
* `CMD ##:##:##:##:...:##` will create a connection to the client with the given ID.

Once `CMD` is run, the server will advise which port to connect to. If the port
reported is 60854, then `telnet localhost 60854` will connect to the client CLI
for the desired client.

### Client CLI Commands
See `CMD` of Admin Interface Commands to raise a client CLI. Once connected
to a client CLI:

* `PING` returns `PONG` from the client.
* `BYE` tells the client to disconnect.
* `TTY` opens a `bash` terminal on the client; server STDIN/STDOUT are routed to the `bash` terminal until the terminal is closed.

## Client

### Configuration

#### client section
Example:
``` JSON
{
"remote": {
    "address": "127.0.0.1",
    "port": 8064,
    "ssl": true
}
}
```

* `address` should be the FQDN of the server.
* `port` is a 2-byte integer. 0-1023 usually require advanced privileges.
* `ssl` should always be true! See Security above.

#### TSL section
See the Server's TSL configuration section.

Instead of the server's certificate and RSA key, supply the client's
certificate and RSA key.

`requestCert` won't do anything either way. clients always request the server
certificate.

### Execution
`node client.js`

## Demonstration Quickstart

Setup:
```
cp conf.server.json.example conf.server.json
cp conf.client.json.example conf.client.json
cd test/x509; ./generate; cd -
```

Run server:
```
node server.js
```

Run client:
```
node client.js
```

Server will inform that a client has connected. Supply commands to server
executable.
