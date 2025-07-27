#!/usr/bin/env python
"""
Independent WebSocket server for inventory notifications
"""
import asyncio
import json
import logging
import os
import sys
import django
from datetime import datetime
import websockets
from websockets.server import serve

# Add Django settings
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_project.settings')
django.setup()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebSocketServer:
    def __init__(self):
        self.clients = set()
        self.message_queue = asyncio.Queue()
        
    async def register_client(self, websocket):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        # Send welcome message
        welcome_message = {
            'type': 'connection_established',
            'message': 'Connected to inventory notifications',
            'timestamp': datetime.now().isoformat()
        }
        await websocket.send(json.dumps(welcome_message))

    async def unregister_client(self, websocket):
        """Unregister a WebSocket client"""
        self.clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

    async def broadcast_message(self, message):
        """Broadcast message to all connected clients"""
        if not self.clients:
            logger.info("No clients connected to broadcast message")
            return
            
        logger.info(f"Broadcasting message to {len(self.clients)} clients: {message}")
        
        # Create a copy of clients to avoid set modification during iteration
        clients_copy = self.clients.copy()
        
        for client in clients_copy:
            try:
                await client.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                logger.info("Client connection closed during broadcast")
                self.clients.discard(client)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")
                self.clients.discard(client)

    async def handle_client_message(self, websocket, message):
        """Handle incoming message from client"""
        try:
            data = json.loads(message)
            logger.info(f"Received message from client: {data}")
            
            # Echo back for testing
            response = {
                'type': 'echo',
                'message': f"Echo: {data.get('message', '')}",
                'timestamp': datetime.now().isoformat()
            }
            await websocket.send(json.dumps(response))
            
        except json.JSONDecodeError:
            error_response = {
                'type': 'error',
                'message': 'Invalid JSON format',
                'timestamp': datetime.now().isoformat()
            }
            await websocket.send(json.dumps(error_response))

    async def client_handler(self, websocket, path):
        """Handle WebSocket client connections"""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                await self.handle_client_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed")
        except Exception as e:
            logger.error(f"Error in client handler: {e}")
        finally:
            await self.unregister_client(websocket)

    async def message_listener(self):
        """Listen for messages from internal queue"""
        logger.info("Listening for internal messages...")
        
        try:
            while True:
                # Wait for messages in the queue
                message = await self.message_queue.get()
                await self.broadcast_message(message)
                self.message_queue.task_done()
        except Exception as e:
            logger.error(f"Message listener error: {e}")

    def add_message_to_queue(self, message_type, data):
        """Add message to internal queue (thread-safe)"""
        message = {
            'type': message_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Put message in queue (non-blocking)
            asyncio.create_task(self.message_queue.put(message))
            logger.info(f"Added message to queue: {message}")
        except Exception as e:
            logger.error(f"Error adding message to queue: {e}")

    async def start_server(self, host='localhost', port=8001):
        """Start the WebSocket server"""
        logger.info(f"Starting WebSocket server on {host}:{port}")
        
        # Start message listener as a background task
        message_task = asyncio.create_task(self.message_listener())
        
        # Start WebSocket server
        server = await serve(
            self.client_handler,
            host,
            port,
            logger=logger
        )
        
        logger.info(f"WebSocket server started on ws://{host}:{port}")
        
        try:
            await server.wait_closed()
        except KeyboardInterrupt:
            logger.info("Shutting down WebSocket server...")
        finally:
            message_task.cancel()
            try:
                await message_task
            except asyncio.CancelledError:
                pass

# Global server instance
ws_server = WebSocketServer()


def send_websocket_notification(message_type, data):
    """
    Function to be called from Django views to send WebSocket notifications
    """
    try:
        ws_server.add_message_to_queue(message_type, data)
    except Exception as e:
        logger.error(f"Error sending WebSocket notification: {e}")


if __name__ == '__main__':
    # Get host and port from environment variables
    host = os.getenv('WEBSOCKET_HOST', '0.0.0.0')
    port = int(os.getenv('WEBSOCKET_PORT', 8001))
    
    try:
        asyncio.run(ws_server.start_server(host, port))
    except KeyboardInterrupt:
        logger.info("WebSocket server stopped")
    except Exception as e:
        logger.error(f"WebSocket server error: {e}")
        sys.exit(1)
