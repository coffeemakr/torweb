[![Build Status](https://travis-ci.org/coffeemakr/torweb.svg)](https://travis-ci.org/coffeemakr/torweb) 
[![Documentation Status](https://readthedocs.org/projects/torweb/badge/?version=latest)](http://torweb.readthedocs.org/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/coffeemakr/torweb/branch/master/graph/badge.svg)](https://codecov.io/gh/coffeemakr/torweb)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/3c7f75b9559340e59a1e5b9a86ce9ed9/badge.svg)](https://www.quantifiedcode.com/app/project/3c7f75b9559340e59a1e5b9a86ce9ed9)

# Torweb

**WARNING:** This application is currently unstable and might or might not work.


Torweb is a webinterface to manage and especially monitor running tor processes.
Currently it supports only monitoring of tor clients and not hidden services or relays.


Application uses:
 * angular-js
 * twisted
 * autobahn (twisted)
 * txtorcon

## Configuration
The configuration file contains entries for every running tor instance that should be monitored.
(Note that even if there are comments in this example, comments are not allowed in this configuration file)
```js
{
  "connections": [
    // Configuration for a tor instance
    {
        "host": "127.0.0.1"  // IP-address or Hostname and ...
        "port": 9051,        // control-port of the running tor.
        "password": "..."    // If set and supported by the server, this password
                             // is used to authenticate the client.[1]
    }
  ]
}
```
* [1]: In the current version of txtorcon, password authentication can't be used if cookie authentication is supported by the server. 


## Usage
Clone repository and run:
```sh
./prepare.sh
./run.sh
```
The server should start and run at `127.0.0.1:8082`

## Screenshots
### Circuit List 
![Screenshot Circuit List](screenshot_circuits.png)

### Circuit Details 
![Screenshot Circuit Details](screenshot_circuit.png)

### Router Details
![Screenshot Circuit List](screenshot_router.png)

### Streams
![Screenshot Circuit List](screenshot_streams.png)
