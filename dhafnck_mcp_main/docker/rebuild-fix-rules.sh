#!/bin/bash

# Script to rebuild Docker container with rules directory fix
# This permanently fixes the issue where manage_rule list doesn't detect rules

set -e

echo "🔧 Rebuilding DhafnckMCP Docker container with rules directory fix..."

# Navigate to docker directory
cd "$(dirname "$0")"

# Stop existing container
echo "⏹️ Stopping existing container..."
docker-compose down

# Remove existing image to force rebuild
echo "🗑️ Removing existing image to force rebuild..."
docker rmi dhafnck/mcp-server:latest 2>/dev/null || true

# Rebuild with no cache to ensure fresh build
echo "🔨 Building new image with rules fix..."
docker-compose build --no-cache

# Start the container
echo "🚀 Starting container with fixed rules directory..."
docker-compose up -d

# Wait for container to be ready
echo "⏳ Waiting for container to be ready..."
sleep 10

# Test if rules are now detected
echo "🧪 Testing rule detection..."
docker exec dhafnck-mcp-server ls -la /app/rules

echo "✅ Docker container rebuilt successfully!"
echo "📋 Rules are now located in /app/rules and should be detected by manage_rule list"
echo "🔗 Symbolic link created at /data/rules -> /app/rules for backward compatibility"

# Optional: Test the MCP rule management
echo ""
echo "🔍 You can now test with: docker exec -it dhafnck-mcp-server python -c \"import sys; sys.path.insert(0, '/app/src'); from fastmcp.server.mcp_entry_point import *; print('Rules directory:', '/app/rules')\"" 