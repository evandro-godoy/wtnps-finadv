"""
WebSocket connection manager for FastAPI.

Manages multiple WebSocket client connections and broadcasts messages.
"""

import logging
from typing import List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket client connections."""
    
    def __init__(self):
        """Initialize WebSocket manager."""
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection to register
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection from active connections.
        
        Args:
            websocket: WebSocket connection to remove
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send a message to a specific WebSocket client.
        
        Args:
            message: Message data to send (will be JSON serialized)
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """
        Broadcast a message to all connected WebSocket clients.
        
        Args:
            message: Message data to send (will be JSON serialized)
        """
        if not self.active_connections:
            logger.debug("No active WebSocket connections to broadcast to")
            return
        
        logger.debug(f"Broadcasting to {len(self.active_connections)} clients")
        
        # Create a copy of connections list to avoid modification during iteration
        connections = self.active_connections.copy()
        
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                self.disconnect(connection)
    
    async def broadcast_text(self, message: str):
        """
        Broadcast a text message to all connected WebSocket clients.
        
        Args:
            message: Text message to send
        """
        if not self.active_connections:
            return
        
        connections = self.active_connections.copy()
        
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting text to client: {e}")
                self.disconnect(connection)
    
    def get_connection_count(self) -> int:
        """
        Get the number of active WebSocket connections.
        
        Returns:
            Number of active connections
        """
        return len(self.active_connections)
