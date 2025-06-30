"""
MCP Status Tool for Real-time Status Updates

This tool provides comprehensive status information to MCP clients and helps
ensure Cursor's MCP tools status icon updates correctly after Docker reloads.

Author: DevOps Agent
Date: 2025-01-27
Purpose: Provide real-time status updates for MCP clients
"""

import logging
import time
from typing import Dict, Any
from datetime import datetime

from fastmcp.server.context import Context
from .connection_manager import get_connection_manager
from .connection_status_broadcaster import get_status_broadcaster

logger = logging.getLogger(__name__)


async def get_mcp_status(ctx: Context, include_details: bool = True) -> Dict[str, Any]:
    """
    Get comprehensive MCP server status information
    
    Args:
        ctx: MCP context with session information
        include_details: Whether to include detailed connection information
    
    Returns:
        Comprehensive status information for MCP clients
    """
    try:
        # Get current timestamp
        now = time.time()
        
        # Initialize status response
        status = {
            "timestamp": now,
            "iso_timestamp": datetime.now().isoformat(),
            "session_id": ctx.session_id if ctx else "unknown",
            "server_info": {
                "name": "DhafnckMCP - Task Management & Agent Orchestration",
                "version": "2.1.0",
                "status": "healthy"
            }
        }
        
        # Get connection manager information
        try:
            connection_manager = await get_connection_manager()
            connection_stats = await connection_manager.get_connection_stats()
            reconnection_info = await connection_manager.get_reconnection_info()
            
            status["connection_info"] = {
                "active_connections": connection_stats["connections"]["active_connections"],
                "total_registered": connection_stats["connections"]["total_registered"],
                "stale_connections": connection_stats["connections"]["stale_connections"],
                "server_restart_count": connection_stats["server_info"]["restart_count"],
                "uptime_seconds": connection_stats["server_info"]["uptime_seconds"],
                "recommended_action": reconnection_info["recommended_action"]
            }
            
            # Determine overall server status
            restart_count = connection_stats["server_info"]["restart_count"]
            uptime = connection_stats["server_info"]["uptime_seconds"]
            active_connections = connection_stats["connections"]["active_connections"]
            
            if restart_count > 0 and uptime < 60:
                status["server_info"]["status"] = "restarted"
                status["server_info"]["message"] = "Server recently restarted, reconnection recommended"
            elif active_connections == 0 and uptime > 60:
                status["server_info"]["status"] = "no_clients"
                status["server_info"]["message"] = "Server healthy but no active client connections"
            else:
                status["server_info"]["status"] = "healthy"
                status["server_info"]["message"] = "Server operating normally"
                
            # Add detailed client information if requested
            if include_details and connection_stats.get("active_clients"):
                status["active_clients"] = connection_stats["active_clients"]
                
        except Exception as e:
            logger.error(f"Error getting connection manager info: {e}")
            status["connection_info"] = {"error": str(e)}
            status["server_info"]["status"] = "degraded"
            status["server_info"]["message"] = f"Connection manager error: {e}"
        
        # Get status broadcaster information
        try:
            status_broadcaster = await get_status_broadcaster()
            last_broadcast = status_broadcaster.get_last_status()
            client_count = status_broadcaster.get_client_count()
            
            status["broadcast_info"] = {
                "registered_clients": client_count,
                "last_broadcast": last_broadcast,
                "broadcasting_active": True
            }
            
        except Exception as e:
            logger.error(f"Error getting status broadcaster info: {e}")
            status["broadcast_info"] = {
                "error": str(e),
                "broadcasting_active": False
            }
        
        # Add authentication status
        try:
            import os
            status["auth_info"] = {
                "enabled": os.environ.get("DHAFNCK_AUTH_ENABLED", "true").lower() == "true",
                "mvp_mode": os.environ.get("DHAFNCK_MVP_MODE", "false").lower() == "true"
            }
        except Exception:
            status["auth_info"] = {"enabled": False, "mvp_mode": False}
        
        # Add Docker/container information
        try:
            import os
            status["container_info"] = {
                "is_docker": os.path.exists("/.dockerenv"),
                "transport": os.environ.get("FASTMCP_TRANSPORT", "stdio"),
                "host": os.environ.get("FASTMCP_HOST", "localhost"),
                "port": os.environ.get("FASTMCP_PORT", "8000")
            }
        except Exception:
            status["container_info"] = {"error": "Could not determine container info"}
        
        # Add tools availability check
        status["tools_info"] = {
            "available": True,  # If this tool is running, tools are available
            "last_check": now,
            "tool_count": "unknown"  # Could be enhanced to count actual tools
        }
        
        # Add recommendations based on status
        recommendations = []
        
        if status["server_info"]["status"] == "restarted":
            recommendations.append("Use Cursor MCP toggle: Settings → Extensions → MCP → Toggle dhafnck_mcp_http OFF/ON")
            recommendations.append("Alternative: Restart Cursor completely")
            
        elif status["server_info"]["status"] == "no_clients":
            recommendations.append("Check Cursor MCP configuration in .cursor/mcp.json")
            recommendations.append("Verify MCP server URL: http://localhost:8000/mcp/")
            
        elif status["connection_info"].get("stale_connections", 0) > 0:
            recommendations.append("Some connections are stale, consider reconnecting")
            
        status["recommendations"] = recommendations
        
        logger.info(f"MCP status check completed for session {ctx.session_id if ctx else 'unknown'}")
        return status
        
    except Exception as e:
        logger.error(f"Error in get_mcp_status: {e}")
        return {
            "timestamp": time.time(),
            "session_id": ctx.session_id if ctx else "unknown",
            "server_info": {
                "status": "error",
                "message": f"Status check failed: {e}"
            },
            "error": str(e)
        }


async def register_for_status_updates(ctx: Context) -> Dict[str, Any]:
    """
    Register the current session for real-time status updates
    
    Args:
        ctx: MCP context with session information
    
    Returns:
        Registration confirmation and status
    """
    try:
        if not ctx or not ctx.session_id:
            return {
                "success": False,
                "error": "No valid session ID for registration"
            }
        
        # Register with status broadcaster
        status_broadcaster = await get_status_broadcaster()
        await status_broadcaster.register_client(ctx.session_id)
        
        # Register with connection manager
        connection_manager = await get_connection_manager()
        await connection_manager.register_connection(
            ctx.session_id,
            {"name": "cursor", "version": "unknown", "type": "mcp_client"}
        )
        
        logger.info(f"Session {ctx.session_id} registered for status updates")
        
        return {
            "success": True,
            "session_id": ctx.session_id,
            "message": "Successfully registered for status updates",
            "update_interval": 30,  # seconds
            "immediate_events": ["server_restart", "tools_unavailable"]
        }
        
    except Exception as e:
        logger.error(f"Error registering for status updates: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def register_mcp_status_tools(server):
    """Register MCP status tools with the FastMCP server"""
    
    @server.tool(
        name="get_mcp_status",
        description="Get comprehensive MCP server status and connection information"
    )
    async def mcp_status_tool(ctx: Context, include_details: bool = True) -> str:
        """
        Get comprehensive MCP server status information
        
        This tool provides detailed information about:
        - Server health and uptime
        - Connection statistics and client information
        - Authentication and container status
        - Tools availability and recommendations
        - Real-time status broadcasting information
        
        Args:
            include_details: Include detailed connection and client information
        
        Returns:
            Formatted status report with recommendations for connection issues
        """
        status_info = await get_mcp_status(ctx, include_details)
        
        # Format the response for better readability
        server_status = status_info.get("server_info", {}).get("status", "unknown")
        status_emoji = {
            "healthy": "✅",
            "restarted": "🔄",
            "no_clients": "📡",
            "degraded": "⚠️",
            "error": "🚨"
        }
        
        emoji = status_emoji.get(server_status, "❓")
        response = f"{emoji} **MCP Server Status: {server_status.title()}**\n\n"
        
        # Server information
        server_info = status_info.get("server_info", {})
        response += "**Server Information:**\n"
        response += f"- Name: {server_info.get('name', 'Unknown')}\n"
        response += f"- Version: {server_info.get('version', 'Unknown')}\n"
        response += f"- Status: {server_info.get('status', 'Unknown')}\n"
        if server_info.get("message"):
            response += f"- Message: {server_info['message']}\n"
        response += f"- Timestamp: {status_info.get('iso_timestamp', 'Unknown')}\n\n"
        
        # Connection information
        conn_info = status_info.get("connection_info", {})
        if "error" not in conn_info:
            response += "**Connection Information:**\n"
            response += f"- Active Connections: {conn_info.get('active_connections', 0)}\n"
            response += f"- Total Registered: {conn_info.get('total_registered', 0)}\n"
            response += f"- Stale Connections: {conn_info.get('stale_connections', 0)}\n"
            response += f"- Server Restarts: {conn_info.get('server_restart_count', 0)}\n"
            response += f"- Uptime: {conn_info.get('uptime_seconds', 0):.1f} seconds\n"
            response += f"- Recommended Action: {conn_info.get('recommended_action', 'continue')}\n\n"
        else:
            response += f"**Connection Error:** {conn_info['error']}\n\n"
        
        # Broadcasting information
        broadcast_info = status_info.get("broadcast_info", {})
        if broadcast_info.get("broadcasting_active"):
            response += "**Real-time Updates:**\n"
            response += f"- Broadcasting Active: ✅\n"
            response += f"- Registered Clients: {broadcast_info.get('registered_clients', 0)}\n"
            if broadcast_info.get("last_broadcast"):
                last_broadcast = broadcast_info["last_broadcast"]
                response += f"- Last Broadcast: {last_broadcast.get('event_type', 'unknown')} "
                response += f"({last_broadcast.get('server_status', 'unknown')})\n"
            response += "\n"
        
        # Authentication and container info
        auth_info = status_info.get("auth_info", {})
        container_info = status_info.get("container_info", {})
        response += "**Configuration:**\n"
        response += f"- Authentication: {'Enabled' if auth_info.get('enabled') else 'Disabled'}\n"
        response += f"- MVP Mode: {'Yes' if auth_info.get('mvp_mode') else 'No'}\n"
        response += f"- Container: {'Docker' if container_info.get('is_docker') else 'Local'}\n"
        response += f"- Transport: {container_info.get('transport', 'unknown')}\n"
        response += f"- Endpoint: {container_info.get('host', 'localhost')}:{container_info.get('port', '8000')}\n\n"
        
        # Active clients details
        if include_details and status_info.get("active_clients"):
            response += "**Active Clients:**\n"
            for client in status_info["active_clients"]:
                response += f"- {client.get('client_name', 'unknown')} "
                response += f"(v{client.get('client_version', '?')})\n"
                response += f"  Session: {client.get('session_id', 'unknown')}\n"
                response += f"  Connected: {client.get('connection_age_seconds', 0):.1f}s ago\n"
                response += f"  Health Checks: {client.get('health_checks', 0)}\n"
            response += "\n"
        
        # Recommendations
        recommendations = status_info.get("recommendations", [])
        if recommendations:
            response += "**💡 Recommendations:**\n"
            for rec in recommendations:
                response += f"- {rec}\n"
            response += "\n"
        
        # Quick actions
        response += "**🔧 Quick Actions:**\n"
        response += "- Check connection: Call `connection_health_check` tool\n"
        response += "- Register for updates: Call `register_for_status_updates` tool\n"
        response += "- Server health: Visit http://localhost:8000/health\n"
        
        return response
    
    @server.tool(
        name="register_for_status_updates", 
        description="Register current session for real-time MCP status updates"
    )
    async def register_status_updates_tool(ctx: Context) -> str:
        """
        Register the current MCP session for real-time status updates
        
        This ensures that your Cursor MCP tools status icon will receive
        immediate notifications about server restarts, connection issues,
        and tools availability changes.
        
        Returns:
            Registration confirmation and update configuration
        """
        result = await register_for_status_updates(ctx)
        
        if result.get("success"):
            response = "✅ **Successfully Registered for Status Updates**\n\n"
            response += f"**Session Information:**\n"
            response += f"- Session ID: {result.get('session_id', 'unknown')}\n"
            response += f"- Update Interval: {result.get('update_interval', 30)} seconds\n"
            response += f"- Immediate Events: {', '.join(result.get('immediate_events', []))}\n\n"
            response += "**What This Means:**\n"
            response += "- Your MCP tools status icon will update automatically\n"
            response += "- You'll receive immediate notifications on server restarts\n"
            response += "- Connection issues will be detected and reported\n"
            response += "- Tools availability changes will be broadcasted\n\n"
            response += "**Next Steps:**\n"
            response += "- Your session is now monitored for connection health\n"
            response += "- If the server restarts, you'll be notified to reconnect\n"
            response += "- Use the `get_mcp_status` tool to check current status anytime\n"
        else:
            response = "❌ **Registration Failed**\n\n"
            response += f"**Error:** {result.get('error', 'Unknown error')}\n\n"
            response += "**Troubleshooting:**\n"
            response += "- Ensure you have a valid MCP session\n"
            response += "- Check server logs for connection issues\n"
            response += "- Try the `connection_health_check` tool for diagnostics\n"
        
        return response
    
    logger.info("MCP status tools registered successfully")
    return [mcp_status_tool, register_status_updates_tool] 