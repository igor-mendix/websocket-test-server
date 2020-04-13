import asyncio
import websockets
import os

CONNECTED_CLIENTS = set()


def escape(message):
    replacements = {
        '\r': '\\r',
        '\n': '\\n',
        '\t': '\\t',
    }

    for find, replace in replacements.items():
        message = message.replace(find, replace)

    return message


async def handler(websocket, path):
    CONNECTED_CLIENTS.add(websocket)

    address = {
        'host': websocket.remote_address[0],
        'port': websocket.remote_address[1],
    }

    try:
        print('Client connected ({host}:{port})'.format(**address))

        async for message in websocket:
            print('Client message received ({host}:{port}): {message}'.format(**address, message=escape(message)))

            other_clients = filter(lambda client: client != websocket, CONNECTED_CLIENTS)

            await asyncio.gather(
                *[websocket.send(message) for websocket in other_clients],
                return_exceptions=False,
            )
    except websockets.ConnectionClosedError:
        pass
    finally:
        print('Client disconnected ({host}:{port})'.format(**address))
        CONNECTED_CLIENTS.remove(websocket)


def main():
    host = os.environ['HOST'] if 'HOST' in os.environ else '0.0.0.0'
    port = int(os.environ['PORT'])

    event_loop = asyncio.get_event_loop()

    event_loop.run_until_complete(websockets.serve(handler, host, port))

    event_loop.run_forever()


if __name__ == '__main__':
    main()
