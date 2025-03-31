import asyncio
import websockets
import sys
import logging
from urllib.parse import urlparse
import datetime
import argparse

def get_timestamp():
    """Return current timestamp in a readable format."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

async def receive_messages(websocket):
    """Listen for incoming messages and print them."""
    try:
        while True:
            message = await websocket.recv()
            timestamp = get_timestamp()
            print(f"[{timestamp}] Received message: {message}")
    except websockets.ConnectionClosed:
        timestamp = get_timestamp()
        print(f"[{timestamp}] Connection closed")

async def send_messages(websocket):
    """Send messages from keyboard input."""
    try:
        while True:
            message = await asyncio.get_event_loop().run_in_executor(
                None, lambda: input("Enter message (or 'exit' to quit): ")
            )
            
            if message.lower() == 'exit':
                timestamp = get_timestamp()
                print(f"[{timestamp}] Exiting...")
                break
                
            await websocket.send(message)
            timestamp = get_timestamp()
            print(f"[{timestamp}] Sent: {message}")
    except asyncio.CancelledError:
        pass

async def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='WebSocket Client')
    parser.add_argument('url', nargs='?',
                        help='WebSocket server URL, e.g. wss://example.com')
    parser.add_argument('--no-keepalive', action='store_true', 
                        help='Disable keepalive pings')
    parser.add_argument('--ping-interval', type=int, default=30,
                        help='Keepalive ping interval in seconds (default: 30)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)
    
    # Get server URL from args
    server_url = args.url
    
    # Validate the URL
    parsed_url = urlparse(server_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        print(f"Error: Invalid URL format: {server_url}")
        print("URL should have format: wss://hostname[:port][/path]")
        return
        
    timestamp = get_timestamp()
    print(f"[{timestamp}] Connecting to WebSocket server at {server_url}")
    
    try:
        # Create connection with longer timeout and disable certificate verification if needed
        async with websockets.connect(
            server_url,
            ssl=parsed_url.scheme == "wss",
            open_timeout=30  # Longer timeout for slow connections
        ) as websocket:
            timestamp = get_timestamp()
            print(f"[{timestamp}] Connected to {server_url}")
            
            # Configure keepalive settings
            if args.no_keepalive:
                websocket.ping_interval = None
                timestamp = get_timestamp()
                print(f"[{timestamp}] Keepalive pings disabled")
            else:
                ping_interval = args.ping_interval
                websocket.ping_interval = ping_interval
                timestamp = get_timestamp()
                print(f"[{timestamp}] Keepalive ping interval set to {ping_interval} seconds")
            receive_task = asyncio.create_task(receive_messages(websocket))
            send_task = asyncio.create_task(send_messages(websocket))
            
            # Wait for either task to complete
            done, pending = await asyncio.wait(
                [receive_task, send_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel the remaining task
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                    
    except ConnectionRefusedError:
        timestamp = get_timestamp()
        print(f"[{timestamp}] Failed to connect to {server_url}. Is the server running?")
    except websockets.InvalidURI as e:
        timestamp = get_timestamp()
        print(f"[{timestamp}] Invalid WebSocket URI: {server_url}")
        print(f"[{timestamp}] Error details: {e}")
        print(f"[{timestamp}] URI format should be: wss://hostname[:port][/path] for secure or ws://hostname[:port][/path] for insecure")
    except websockets.WebSocketException as e:
        timestamp = get_timestamp()
        print(f"[{timestamp}] WebSocket error: {e}")
    except Exception as e:
        timestamp = get_timestamp()
        print(f"[{timestamp}] Connection error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        timestamp = get_timestamp()
        print(f"\n[{timestamp}] Client terminated by user")
    except SystemExit:
        # Handle when argparse exits the program (e.g., with --help)
        pass
