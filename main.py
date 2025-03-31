import asyncio
import websockets
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

async def handler(websocket):
    CONNECTED_CLIENTS.add(websocket)
    address = {
        'host': websocket.remote_address[0],
        'port': websocket.remote_address[1],
    }
    logging.info(f"Client connected ({address['host']}:{address['port']})")
    try:
        async for message in websocket:
            logging.info(f"Client message received ({address['host']}:{address['port']}): {escape(message)}")
            other_clients = {client for client in CONNECTED_CLIENTS if client != websocket}
            if other_clients:
                 await asyncio.gather(
                    *[client.send(message) for client in other_clients],
                    return_exceptions=False,
                )
    except websockets.ConnectionClosedError as e:
         logging.info(f"Client connection closed normally ({address['host']}:{address['port']}): {e.code} {e.reason}")
    except Exception as e:
        logging.error(f"Error handling client ({address['host']}:{address['port']}): {e}", exc_info=True)
    finally:
        logging.info(f"Client disconnected ({address['host']}:{address['port']})")
        CONNECTED_CLIENTS.remove(websocket)

async def main_async():
    """Sets up and runs the WebSocket server asynchronously"""
    host = os.environ.get('HOST', '0.0.0.0')
    try:
        port = int(os.environ['PORT'])
    except KeyError:
        logging.error("PORT environment variable not set")
        return
    except ValueError:
         logging.error(f"Invalid PORT value: {os.environ.get('PORT')}. Must be an integer")
         return

    disable_keepalive_str = os.environ.get('DISABLE_KEEPALIVE', 'false').lower()
    disable_keepalive = disable_keepalive_str in ('true', '1', 'yes')

    keepalive_params = {}
    if disable_keepalive:
        logging.info("Keepalives disabled via DISABLE_KEEPALIVE environment variable")
        keepalive_params = {'ping_interval': None, 'ping_timeout': None}
    else:
        logging.info("Keepalives enabled (default). Set DISABLE_KEEPALIVE=true to disable")

    logging.info(f"Starting WebSocket server on {host}:{port}...")

    try:
        async with websockets.serve(handler, host, port, **keepalive_params) as server:
            await server.wait_closed()
    except OSError as e:
         logging.error(f"Failed to start server on {host}:{port}: {e}")
    except Exception as e:
        logging.error(f"Server error: {e}", exc_info=True)
    finally:
        logging.info("WebSocket server stopped")

def main():
    """Synchronous entry point"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logging.info("Server stopped by user (KeyboardInterrupt)")

if __name__ == '__main__':
    main()
