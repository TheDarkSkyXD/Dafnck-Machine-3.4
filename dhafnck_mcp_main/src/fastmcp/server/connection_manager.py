"""
Connection Manager for MCP Server

This module handles MCP client connections, health monitoring, and automatic reconnection
to resolve issues where Cursor needs to be restarted after Docker rebuilds.

Author: DevOps Agent
Date: 2025-01-27
Purpose: Improve MCP client connection reliability and handle Docker rebuild scenarios
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ConnectionInfo:
    """Information about an MCP client connection"""
    session_id: str
    client_info: Dict[str, Any]
    connected_at: datetime
    last_activity: datetime
    health_check_count: int = 0
    is_healthy: bool = True
    client_capabilities: Dict[str, Any] = None
    
    def update_activity(self):
        """Update the last activity timestamp"""
        self.last_activity = datetime.now()
        
    def is_stale(self, timeout_minutes: int = 30) -> bool:
        """Check if connection is stale (no activity for timeout period)"""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)


class ConnectionManager:
    """Manages MCP client connections with health monitoring and reconnection support"""
    
    def __init__(self):
        self.connections: Dict[str, ConnectionInfo] = {}
        self.server_start_time = datetime.now()
        self.server_restart_count = 0
        self.health_check_interval = 30  # seconds
        self.connection_timeout = 30  # minutes
        self._health_task: Optional[asyncio.Task] = None
        self._running = False
        
    async def start_monitoring(self):
        """Start the connection health monitoring task"""
        if self._running:
            return
            
        self._running = True
        self._health_task = asyncio.create_task(self._health_monitor_loop())
        logger.info("Connection manager started with health monitoring")
        
    async def stop_monitoring(self):
        """Stop the connection health monitoring task"""
        self._running = False
        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass
        logger.info("Connection manager stopped")
        
    async def register_connection(self, session_id: str, client_info: Dict[str, Any], 
                                client_capabilities: Dict[str, Any] = None) -> ConnectionInfo:
        """Register a new MCP client connection"""
        now = datetime.now()
        
        connection = ConnectionInfo(
            session_id=session_id,
            client_info=client_info,
            connected_at=now,
            last_activity=now,
            client_capabilities=client_capabilities or {}
        )
        
        self.connections[session_id] = connection
        logger.info(f"Registered new MCP connection: {session_id} from {client_info.get('name', 'unknown')}")
        
        return connection
        
    async def update_connection_activity(self, session_id: str):
        """Update the last activity time for a connection"""
        if session_id in self.connections:
            self.connections[session_id].update_activity()
            
    async def unregister_connection(self, session_id: str):
        """Unregister an MCP client connection"""
        if session_id in self.connections:
            connection = self.connections.pop(session_id)
            logger.info(f"Unregistered MCP connection: {session_id}")
            return connection
        return None
        
    async def get_connection(self, session_id: str) -> Optional[ConnectionInfo]:
        """Get connection information by session ID"""
        return self.connections.get(session_id)
        
    async def get_active_connections(self) -> Dict[str, ConnectionInfo]:
        """Get all active (non-stale) connections"""
        active = {}
        for session_id, conn in self.connections.items():
            if not conn.is_stale(self.connection_timeout):
                active[session_id] = conn
        return active
        
    async def cleanup_stale_connections(self) -> int:
        """Remove stale connections and return count of removed connections"""
        stale_sessions = []
        
        for session_id, conn in self.connections.items():
            if conn.is_stale(self.connection_timeout):
                stale_sessions.append(session_id)
                
        for session_id in stale_sessions:
            await self.unregister_connection(session_id)
            
        if stale_sessions:
            logger.info(f"Cleaned up {len(stale_sessions)} stale connections")
            
        return len(stale_sessions)
        
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get comprehensive connection statistics"""
        active_connections = await self.get_active_connections()
        
        stats = {
            "server_info": {
                "start_time": self.server_start_time.isoformat(),
                "uptime_seconds": (datetime.now() - self.server_start_time).total_seconds(),
                "restart_count": self.server_restart_count
            },
            "connections": {
                "total_registered": len(self.connections),
                "active_connections": len(active_connections),
                "stale_connections": len(self.connections) - len(active_connections)
            },
            "active_clients": []
        }
        
        for session_id, conn in active_connections.items():
            client_stats = {
                "session_id": session_id,
                "client_name": conn.client_info.get("name", "unknown"),
                "client_version": conn.client_info.get("version", "unknown"),
                "connected_at": conn.connected_at.isoformat(),
                "last_activity": conn.last_activity.isoformat(),
                "connection_age_seconds": (datetime.now() - conn.connected_at).total_seconds(),
                "health_checks": conn.health_check_count,
                "is_healthy": conn.is_healthy,
                "capabilities": list(conn.client_capabilities.keys()) if conn.client_capabilities else []
            }
            stats["active_clients"].append(client_stats)
            
        return stats
        
    async def _health_monitor_loop(self):
        """Background task to monitor connection health"""
        while self._running:
            try:
                # Cleanup stale connections
                await self.cleanup_stale_connections()
                
                # Update health status for active connections
                active_connections = await self.get_active_connections()
                for conn in active_connections.values():
                    conn.health_check_count += 1
                    
                # Log connection statistics periodically
                if len(active_connections) > 0:
                    logger.debug(f"Health check: {len(active_connections)} active connections")
                    
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in connection health monitor: {e}")
                await asyncio.sleep(5)  # Brief pause before retrying
                
    async def handle_server_restart(self):
        """Handle server restart scenarios - mark for client reconnection"""
        self.server_restart_count += 1
        self.server_start_time = datetime.now()
        
        # Mark all existing connections as potentially stale
        for conn in self.connections.values():
            conn.is_healthy = False
            
        logger.info(f"Server restart detected (#{self.server_restart_count}). Existing connections marked for validation.")
        
    async def get_reconnection_info(self) -> Dict[str, Any]:
        """Get information to help clients reconnect after server restart"""
        return {
            "server_restart_count": self.server_restart_count,
            "server_start_time": self.server_start_time.isoformat(),
            "recommended_action": "reconnect" if self.server_restart_count > 0 else "continue",
            "health_endpoint": "/health",
            "mcp_endpoint": "/mcp/",
            "connection_timeout_minutes": self.connection_timeout
        }


# Global connection manager instance
_connection_manager: Optional[ConnectionManager] = None


async def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance"""
    global _connection_manager
    
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
        await _connection_manager.start_monitoring()
        
    return _connection_manager


async def cleanup_connection_manager():
    """Cleanup the global connection manager"""
    global _connection_manager
    
    if _connection_manager:
        await _connection_manager.stop_monitoring()
        _connection_manager = None 