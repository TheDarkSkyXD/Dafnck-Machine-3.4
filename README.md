# 🐳 DhafnckMCP - Docker-Based MCP Server

[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue)](https://github.com/dhafnck/dhafnck_mcp)
[![MCP Server](https://img.shields.io/badge/MCP-Server-green)](https://github.com/dhafnck/dhafnck_mcp)
[![Production Ready](https://img.shields.io/badge/Production-Ready-brightgreen)](https://github.com/dhafnck/dhafnck_mcp)

## 🎯 **What is DhafnckMCP?**

DhafnckMCP is a production-ready Model Context Protocol (MCP) server that runs in Docker containers. It provides comprehensive task management, project orchestration, and multi-agent coordination capabilities through a robust HTTP-based MCP interface.

### 🚀 **Key Features**

- **🐳 Docker-First Architecture**: Complete containerized deployment with Docker Compose
- **📊 Task Management**: Comprehensive task lifecycle with dependencies and subtasks
- **🤖 Multi-Agent Orchestration**: Coordinated agent workflows and role switching
- **🔧 MCP Tools**: Full suite of MCP server tools and utilities
- **📁 Project Management**: Multi-project support with hierarchical organization
- **💾 Persistent Storage**: Flexible data storage with internal/external volume options
- **🔍 Health Monitoring**: Built-in health checks and diagnostic tools
- **⚡ Development Mode**: Streamlined development environment with live logging

## 🚀 **Quick Start**

> **⚡ Get DhafnckMCP running in under 2 minutes!**

### 📋 **Prerequisites**

Before you begin, ensure you have:

| Requirement | Version | Installation Guide |
|-------------|---------|-------------------|
| **Docker Desktop** or **Docker Engine** | 20.10+ | [Get Docker](https://docs.docker.com/get-docker/) |
| **Docker Compose** | v2.0+ | [Install Compose](https://docs.docker.com/compose/install/) |
| **bash** shell | Any recent version | Pre-installed on Linux/macOS, [Git Bash](https://git-scm.com/downloads) for Windows |

**Quick Verification:**
```bash
# Verify your setup
docker --version && docker-compose --version
```

---

### 🏃‍♂️ **Method 1: Express Setup (30 seconds)**

**Perfect for:** First-time users, quick testing, development

```bash
# 1. Clone and navigate
git clone https://github.com/dhafnck/dhafnck_mcp.git
cd dhafnck_mcp_main

# 2. One-command startup (builds and runs automatically)
./scripts/manage-docker.sh start

# 3. Verify it's working
./scripts/manage-docker.sh health
```

**✅ Success!** Your MCP server is now running at: `http://localhost:8000/mcp/`

---

### 🛠️ **Method 2: Step-by-Step Setup**

**Perfect for:** Understanding the process, customization, troubleshooting

#### **Step 1: Get the Code**
```bash
git clone https://github.com/dhafnck/dhafnck_mcp.git
cd dhafnck_mcp_main
```

#### **Step 2: Choose Your Configuration**
```bash
# Option A: Standard setup (recommended)
./scripts/manage-docker.sh start

# Option B: Development mode (with live logs)
./scripts/dev-docker.sh

# Option C: External storage (for data persistence)
docker-compose -f docker/docker-compose.external.yml up -d
```

#### **Step 3: Verify Installation**
```bash
# Health check
./scripts/manage-docker.sh health

# Expected output:
# ✅ Container Status: Running
# ✅ Health Check: Healthy
# ✅ MCP Endpoint: Accessible at http://localhost:8000/mcp/
```

#### **Step 4: View Live Logs (Optional)**
```bash
# Monitor server activity
./scripts/manage-docker.sh logs
```

---

### 🔌 **Connect Your MCP Client**

#### **For Cursor AI Editor**
Add this to your `.cursor/mcp.json`:

```json
{
  "dhafnck_mcp_http": {
    "url": "http://localhost:8000/mcp/",
    "type": "http",
    "headers": {
      "Accept": "application/json, text/event-stream"
    }
  }
}
```

#### **For Other MCP Clients**
Use these connection details:
- **URL**: `http://localhost:8000/mcp/`
- **Type**: `http`
- **Headers**: `{"Accept": "application/json, text/event-stream"}`

---

### 🧪 **Test Your Installation**

#### **Quick Health Check**
```bash
# Test server responsiveness
curl -f http://localhost:8000/health || echo "❌ Server not responding"

# Expected response: {"status": "healthy", "timestamp": "..."}
```

#### **MCP Inspector Test**
```bash
# Test with official MCP Inspector
npx @modelcontextprotocol/inspector \
  '{"dhafnck_mcp_http": {"url": "http://localhost:8000/mcp/", "type": "http", "headers": {"Accept": "application/json, text/event-stream"}}}'
```

#### **Browser Test**
Open your browser and navigate to:
- **Health Check**: http://localhost:8000/health
- **MCP Endpoint**: http://localhost:8000/mcp/

---

### 🎯 **What's Next?**

Now that DhafnckMCP is running, you can:

1. **📊 Explore Task Management**
   ```bash
   # View available MCP tools
   curl http://localhost:8000/mcp/tools
   ```

2. **🤖 Set Up Multi-Agent Workflows**
   - Connect your AI editor (Cursor, VS Code, etc.)
   - Start using MCP tools for task orchestration

3. **📁 Create Your First Project**
   - Use the web interface or MCP tools
   - Set up project structure and tasks

4. **🔧 Customize Configuration**
   - Modify environment variables
   - Set up external storage
   - Configure authentication

---

### 🆘 **Quick Troubleshooting**

| Issue | Quick Fix |
|-------|-----------|
| **Port 8000 in use** | `./scripts/manage-docker.sh stop && ./scripts/manage-docker.sh start` |
| **Container won't start** | `./scripts/manage-docker.sh cleanup && ./scripts/manage-docker.sh start` |
| **Health check fails** | `./scripts/manage-docker.sh logs` to check errors |
| **Permission denied** | `sudo chown -R $USER:$USER .` (Linux/WSL2) |

**Need more help?** Check the [🚨 Troubleshooting](#🚨-troubleshooting) section below.

---

### 📚 **Learning Resources**

- **🐳 [Complete Docker Guide](docker/README_DOCKER.md)** - Detailed Docker documentation
- **🛠️ [Management Scripts](scripts/README_SCRIPT.md)** - All available commands
- **🔧 [Configuration Guide](#🔧-configuration)** - Environment setup
- **📁 [Project Structure](#📁-project-structure)** - Understanding the codebase

## 🛠️ **Docker Management Commands**

### Essential Commands
```bash
# Start the server
./scripts/manage-docker.sh start

# Stop the server
./scripts/manage-docker.sh stop

# Restart the server
./scripts/manage-docker.sh restart

# View live logs
./scripts/manage-docker.sh logs

# Check server health
./scripts/manage-docker.sh health

# View system status
./scripts/manage-docker.sh status

# Open shell in container
./scripts/manage-docker.sh shell

# Complete cleanup and rebuild
./scripts/manage-docker.sh cleanup
```

### Development Commands
```bash
# Start with development logging
./scripts/dev-docker.sh

# Quick rebuild and start
docker system prune -f && docker-compose -f docker/docker-compose.redis.yml down && docker-compose -f docker/docker-compose.redis.yml build --no-cache dhafnck-mcp && ./scripts/manage-docker.sh start

# Check recent logs
docker logs dhafnck-mcp-server | tail -200

# Interactive container access
docker exec -it dhafnck-mcp-server /bin/bash
```

## 🏗️ **Architecture Overview**

### Docker Container Structure
```
dhafnck-mcp-server/
├── /app/                    # Application code
│   ├── src/                 # Source code
│   ├── .venv/               # Python virtual environment
│   └── logs/                # Application logs
├── /data/                   # Persistent data
│   ├── tasks/               # Task management data
│   ├── projects/            # Project configurations
│   ├── contexts/            # Task contexts
│   └── rules/               # Cursor rules and contexts
└── /app/config/             # Configuration files
```

### Network Configuration
- **Container Name**: `dhafnck-mcp-server`
- **HTTP Port**: 8000 (mapped to localhost:8000)
- **MCP Endpoint**: `http://localhost:8000/mcp/`
- **Health Check**: `http://localhost:8000/health`
- **Development Port**: 8001 (development mode only)

### Available MCP Tools
The server provides these MCP tools for task and project management:
- **Task Management**: Create, update, list, and manage tasks
- **Project Orchestration**: Multi-project support and coordination
- **Agent Management**: Agent registration and role switching
- **Context Management**: Intelligent context synchronization
- **Document Management**: Document tracking and organization
- **Rule Management**: Cursor rules and context generation

## 💾 **Data Storage Options**

### Internal Storage (Default)
- Data stored in Docker named volumes
- Survives container restarts
- Managed by Docker

```bash
# Uses internal storage automatically
./scripts/manage-docker.sh start
```

### External Storage
- Data stored in host directories
- Easy backup and direct access
- Survives container removal

```bash
# Start with external storage
docker-compose -f docker/docker-compose.external.yml up -d
```

### Storage Structure
```
data/
├── tasks/                   # Task management data
├── projects/               # Project configurations
├── contexts/               # Task contexts
└── rules/                  # Cursor rules and auto-generated content

logs/
├── fastmcp.log            # Main application log
├── error.log              # Error logs
└── access.log             # HTTP access logs
```

## 🔧 **Configuration**

### Environment Variables
Key configuration options:

```bash
# Core MCP Configuration
FASTMCP_HOST=0.0.0.0
FASTMCP_PORT=8000
FASTMCP_TRANSPORT=streamable-http
FASTMCP_LOG_LEVEL=INFO

# Authentication (disabled in local mode)
DHAFNCK_AUTH_ENABLED=false
DHAFNCK_MVP_MODE=false

# Data Storage
TASKS_JSON_PATH=/data/tasks
PROJECTS_FILE_PATH=/data/projects/projects.json
CURSOR_RULES_DIR=/data/rules
```

### Docker Compose Files
- `docker-compose.yml` - Main production configuration
- `docker-compose.local.yml` - Local development overrides
- `docker-compose.dev.yml` - Development-specific settings
- `docker-compose.redis.yml` - Redis integration
- `docker-compose.external.yml` - External storage configuration

## 🧪 **Development**

### Development Mode
```bash
# Start in development mode
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d

# Or use the development script
./scripts/dev-docker.sh
```

### Testing
```bash
# Run tests in container
docker exec -it dhafnck-mcp-server python -m pytest

# Run with coverage
docker exec -it dhafnck-mcp-server python -m pytest --cov=src

# Run specific test categories
docker exec -it dhafnck-mcp-server python -m pytest tests/task_management/
```

### Debugging
```bash
# View detailed logs
./scripts/manage-docker.sh logs

# Access container shell
./scripts/manage-docker.sh shell

# Check server health
./scripts/manage-docker.sh health

# Monitor resource usage
docker stats dhafnck-mcp-server
```

## 📁 **Project Structure**

```
dhafnck_mcp_main/
├── docker/                           # Docker configuration
│   ├── docker-compose.yml           # Main Docker Compose
│   ├── docker-compose.*.yml         # Environment-specific configs
│   ├── Dockerfile                   # Container build instructions
│   └── README_DOCKER.md             # Detailed Docker documentation
├── scripts/                          # Management scripts
│   ├── manage-docker.sh             # Main Docker management
│   ├── dev-docker.sh                # Development utilities
│   └── diagnose_mcp_connection.sh   # Connection diagnostics
├── src/                              # Source code
│   └── fastmcp/                      # FastMCP implementation
├── tests/                            # Test suites
├── docs/                             # Documentation
├── examples/                         # Usage examples
└── .cursor/                          # AI assistant rules and context
```

## 🔍 **Health Monitoring & Diagnostics**

### Health Checks
```bash
# Quick health check
./scripts/manage-docker.sh health

# Detailed diagnostics
./scripts/diagnose_mcp_connection.sh

# Container status
./scripts/manage-docker.sh status
```

### Log Monitoring
```bash
# Live logs
./scripts/manage-docker.sh logs

# Recent logs
docker logs dhafnck-mcp-server --tail 50

# Error logs only
docker logs dhafnck-mcp-server 2>&1 | grep -i error
```

### Performance Monitoring
```bash
# Resource usage
docker stats dhafnck-mcp-server

# Volume usage
docker volume ls | grep dhafnck

# Network inspection
docker network inspect docker_default
```

## 🚨 **Troubleshooting**

### Common Issues

#### Container Won't Start
```bash
# Check Docker status
docker ps

# Check for port conflicts
netstat -tulpn | grep 8000

# Clean up and restart
./scripts/manage-docker.sh cleanup
./scripts/manage-docker.sh start
```

#### Health Check Failures
```bash
# Verify port accessibility
nc -z localhost 8000

# Check container logs
./scripts/manage-docker.sh logs

# Restart container
./scripts/manage-docker.sh restart
```

#### Permission Issues (Linux/WSL2)
```bash
# Fix directory permissions
sudo chown -R $USER:$USER docker/data docker/logs

# Restart WSL2 (if needed)
wsl --shutdown
```

### Diagnostic Tools
```bash
# Full system diagnostics
./scripts/diagnose_mcp_connection.sh

# Container inspection
docker inspect dhafnck-mcp-server

# Volume inspection
docker volume inspect docker_dhafnck_data
```

## 📚 **Documentation**

### Docker-Specific Documentation
- **[Complete Docker Guide](docker/README_DOCKER.md)** - Comprehensive Docker documentation
- **[Script Documentation](scripts/README_SCRIPT.md)** - All management scripts explained

### Development Documentation
- **[Development Setup](docs/)** - Development environment setup
- **[API Documentation](docs/)** - MCP API reference
- **[Testing Guide](tests/)** - Testing procedures and examples

## 🌟 **Production Deployment**

### Production Checklist
- [ ] Configure external storage for data persistence
- [ ] Set up proper logging and monitoring
- [ ] Configure authentication if needed
- [ ] Set up backup procedures
- [ ] Configure SSL/TLS for HTTPS
- [ ] Set resource limits and health checks

### Production Commands
```bash
# Production deployment
docker-compose -f docker/docker-compose.yml up -d

# With external storage
docker-compose -f docker/docker-compose.external.yml up -d

# Health monitoring
watch -n 5 './scripts/manage-docker.sh health'
```

## 🔐 **Security**

### Security Features
- **Containerized Isolation**: Application runs in isolated Docker container
- **Configurable Authentication**: Can be enabled for production environments
- **Network Security**: Configurable network policies and port restrictions
- **Data Encryption**: Supports encrypted data volumes
- **Audit Logging**: Comprehensive logging for security monitoring

### Security Configuration
```bash
# Enable authentication
DHAFNCK_AUTH_ENABLED=true

# Configure secure ports
FASTMCP_PORT=8443  # HTTPS port

# Enable audit logging
FASTMCP_LOG_LEVEL=DEBUG
```

## 🚀 **Performance**

### Current Performance
- **Scale**: 100-1000 RPS (containerized Python)
- **Latency**: <100ms for most operations
- **Memory**: ~256MB base usage
- **CPU**: ~0.1-0.5 cores under normal load

### Performance Optimization
- **Resource Limits**: Configurable memory and CPU limits
- **Caching**: Built-in caching for frequently accessed data
- **Connection Pooling**: Efficient connection management
- **Async Processing**: Non-blocking request handling

## 🤝 **Contributing**

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make changes and test with Docker
4. Run tests: `docker exec -it dhafnck-mcp-server python -m pytest`
5. Submit a pull request

### Code Quality
- **Linting**: Ruff for code quality
- **Type Checking**: mypy for static analysis
- **Testing**: pytest with comprehensive coverage
- **Containerization**: All changes tested in Docker environment

## 📄 **License**

This project is licensed under the MIT License. See the LICENSE file for details.

---

## 🎯 **Current Status**

### ✅ **Production Ready**
- **Docker Integration**: Complete containerized deployment
- **MCP Server**: Fully functional HTTP-based MCP server
- **Task Management**: Comprehensive task and project management
- **Development Tools**: Complete development and debugging environment
- **Documentation**: Comprehensive guides and troubleshooting

### 🚀 **Quick Start Summary**
```bash
# Get started in 3 commands
git clone https://github.com/dhafnck/dhafnck_mcp.git
cd dhafnck_mcp_main
./scripts/manage-docker.sh start

# Your MCP server is now running at: http://localhost:8000/mcp/
```

---

**Last Updated**: 2025-01-27  
**Version**: 2.0.0 (Docker-based)  
**Status**: Production Ready  
**Docker Compatibility**: 20.10+, Docker Compose v2.0+ 

---

### 🔗 **Quick Links**
- **MCP Server**: http://localhost:8000/mcp/
- **Health Check**: http://localhost:8000/health
- **Docker Documentation**: [docker/README_DOCKER.md](docker/README_DOCKER.md)
- **Script Documentation**: [scripts/README_SCRIPT.md](scripts/README_SCRIPT.md)