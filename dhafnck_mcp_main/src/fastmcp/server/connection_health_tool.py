"""
Connection Health Check Tool for MCP Server

This tool provides detailed connection health information and helps diagnose
issues where Cursor needs to be restarted after Docker rebuilds.

Author: DevOps Agent
Date: 2025-01-27
Purpose: Improve MCP connection diagnostics and reconnection guidance
"""

import logging
import time
from typing import Dict, Any
from datetime import datetime

from fastmcp.server.context import Context
from .connection_manager import get_connection_manager

logger = logging.getLogger(__name__)


async def connection_health_check(ctx: Context) -> Dict[str, Any]:
    """
    Comprehensive connection health check for MCP clients
    
    Returns detailed information about:
    - Server restart status
    - Active connections
    - Connection statistics
    - Reconnection recommendations
    """
    try:
        connection_manager = await get_connection_manager()
        
        # Update activity for current session
        if ctx.session_id:
            await connection_manager.update_connection_activity(ctx.session_id)
        
        # Get comprehensive connection stats
        connection_stats = await connection_manager.get_connection_stats()
        reconnection_info = await connection_manager.get_reconnection_info()
        
        # Build health response
        health_info = {
            "timestamp": datetime.now().isoformat(),
            "current_session_id": ctx.session_id,
            "server_status": "healthy",
            "connection_manager": connection_stats,
            "reconnection_info": reconnection_info
        }
        
        # Determine overall health status
        active_connections = connection_stats["connections"]["active_connections"]
        restart_count = connection_stats["server_info"]["restart_count"]
        
        if restart_count > 0 and active_connections == 0:
            health_info["server_status"] = "restarted_no_clients"
            health_info["recommendation"] = "Server was restarted. MCP clients should reconnect."
        elif restart_count > 0:
            health_info["server_status"] = "restarted_with_clients"
            health_info["recommendation"] = "Server was restarted but has active connections."
        elif active_connections == 0:
            health_info["server_status"] = "no_clients"
            health_info["recommendation"] = "No active MCP clients connected."
        else:
            health_info["recommendation"] = "All connections healthy."
        
        # Add warnings for common issues
        warnings = []
        
        if restart_count > 0:
            warnings.append(f"Server has been restarted {restart_count} time(s). MCP clients may need to reconnect.")
        
        if connection_stats["connections"]["stale_connections"] > 0:
            warnings.append(f"{connection_stats['connections']['stale_connections']} stale connections detected.")
        
        if active_connections == 0 and ctx.session_id:
            warnings.append("No active connections detected, but current session exists. Connection state may be inconsistent.")
        
        if warnings:
            health_info["warnings"] = warnings
        
        # Add troubleshooting steps
        health_info["troubleshooting"] = {
            "cursor_reconnection": [
                "1. Toggle MCP server off in Cursor settings",
                "2. Wait 2-3 seconds", 
                "3. Toggle MCP server back on",
                "4. Check if tools are available again"
            ],
            "docker_rebuild": [
                "1. After rebuilding Docker containers",
                "2. The MCP server gets a new container ID",
                "3. Cursor's HTTP connection becomes stale",
                "4. Use the toggle method above to reconnect"
            ],
            "alternative_methods": [
                "1. Restart Cursor completely (slower but reliable)",
                "2. Use Cursor Developer Tools to check MCP connection status",
                "3. Check Docker container status: docker ps",
                "4. Verify server health: curl http://localhost:8000/health"
            ]
        }
        
        logger.info(f"Connection health check completed for session {ctx.session_id}")
        return health_info
        
    except Exception as e:
        logger.error(f"Connection health check failed: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "server_status": "error",
            "error": str(e),
            "recommendation": "Connection health check failed. Check server logs for details.",
            "troubleshooting": {
                "immediate_steps": [
                    "1. Check if Docker container is running: docker ps",
                    "2. Check server logs: docker logs dhafnck-mcp-server",
                    "3. Verify server health: curl http://localhost:8000/health",
                    "4. Restart MCP server if needed"
                ]
            }
        }


def register_connection_health_tool(server):
    """Register the connection health check tool with the FastMCP server"""
    
    @server.tool(
        name="connection_health_check",
        description="Check MCP connection health and get reconnection guidance"
    )
    async def connection_health_tool(ctx: Context) -> str:
        """
        Check MCP connection health and get troubleshooting guidance
        
        This tool helps diagnose connection issues, especially after Docker rebuilds,
        and provides specific steps to reconnect without restarting Cursor.
        
        Returns detailed information about:
        - Server restart status
        - Active MCP connections
        - Connection statistics and health
        - Step-by-step reconnection instructions
        - Troubleshooting guidance for common issues
        """
        health_info = await connection_health_check(ctx)
        
        # Format the response for better readability
        status_emoji = {
            "healthy": "✅",
            "restarted_no_clients": "🔄",
            "restarted_with_clients": "⚠️",
            "no_clients": "📡",
            "error": "🚨"
        }
        
        emoji = status_emoji.get(health_info.get("server_status", "error"), "❓")
        status = health_info.get("server_status", "unknown").replace("_", " ").title()
        
        response = f"{emoji} **Connection Health Status: {status}**\n\n"
        
        # Current session info
        response += "**Current Session:**\n"
        response += f"- Session ID: {health_info.get('current_session_id', 'none')}\n"
        response += f"- Timestamp: {health_info.get('timestamp', 'unknown')}\n\n"
        
        # Server information
        server_info = health_info.get("connection_manager", {}).get("server_info", {})
        response += "**Server Information:**\n"
        response += f"- Uptime: {server_info.get('uptime_seconds', 0):.1f} seconds\n"
        response += f"- Restart Count: {server_info.get('restart_count', 0)}\n"
        response += f"- Start Time: {server_info.get('start_time', 'unknown')}\n\n"
        
        # Connection statistics
        conn_info = health_info.get("connection_manager", {}).get("connections", {})
        response += "**Connection Statistics:**\n"
        response += f"- Active Connections: {conn_info.get('active_connections', 0)}\n"
        response += f"- Total Registered: {conn_info.get('total_registered', 0)}\n"
        response += f"- Stale Connections: {conn_info.get('stale_connections', 0)}\n\n"
        
        # Active clients
        active_clients = health_info.get("connection_manager", {}).get("active_clients", [])
        if active_clients:
            response += "**Active Clients:**\n"
            for client in active_clients:
                response += f"- {client.get('client_name', 'unknown')} (v{client.get('client_version', '?')})\n"
                response += f"  Connected: {client.get('connection_age_seconds', 0):.1f}s ago\n"
                response += f"  Health Checks: {client.get('health_checks', 0)}\n"
            response += "\n"
        
        # Recommendation
        if health_info.get("recommendation"):
            response += f"**💡 Recommendation:**\n{health_info['recommendation']}\n\n"
        
        # Warnings
        if health_info.get("warnings"):
            response += "**⚠️ Warnings:**\n"
            for warning in health_info["warnings"]:
                response += f"- {warning}\n"
            response += "\n"
        
        # Troubleshooting steps
        troubleshooting = health_info.get("troubleshooting", {})
        
        if "cursor_reconnection" in troubleshooting:
            response += "**🔄 Quick Cursor Reconnection (Recommended):**\n"
            for step in troubleshooting["cursor_reconnection"]:
                response += f"{step}\n"
            response += "\n"
        
        if "docker_rebuild" in troubleshooting:
            response += "**🐳 After Docker Rebuild:**\n"
            for step in troubleshooting["docker_rebuild"]:
                response += f"{step}\n"
            response += "\n"
        
        if "alternative_methods" in troubleshooting:
            response += "**🛠️ Alternative Methods:**\n"
            for step in troubleshooting["alternative_methods"]:
                response += f"{step}\n"
            response += "\n"
        
        if "immediate_steps" in troubleshooting:
            response += "**🚨 Immediate Troubleshooting:**\n"
            for step in troubleshooting["immediate_steps"]:
                response += f"{step}\n"
            response += "\n"
        
        # Reconnection info
        reconnection_info = health_info.get("reconnection_info", {})
        if reconnection_info.get("recommended_action") == "reconnect":
            response += "**🔗 Reconnection Required:**\n"
            response += f"Server was restarted. Please use the quick reconnection steps above.\n\n"
        
        # Error details
        if health_info.get("error"):
            response += f"**🚨 Error Details:**\n{health_info['error']}\n\n"
        
        return response
    
    logger.info("Connection health check tool registered successfully")
    return connection_health_tool 