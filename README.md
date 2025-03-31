# WebSocket Test Server

This server is a simple docker container that was designed to test applications that interact with websockets.

Every message received from a connected client is broadcast to all other connected clients (but not echoed back).

This makes it simple to test the interaction of an application with an API that is provided using websockets.

As this is designed to be used in a test suite, it is not suitable for production use.

## Usage

```sh
docker run --rm -p 5000:5000 -e PORT=5000 igormendix/websocket-test-server
```

```sh
docker run --rm -p 5000:5000 -e PORT=5000 -e DISABLE_KEEPALIVE=true igormendix/websocket-test-server
```
