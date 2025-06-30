---
description: 
globs: 
alwaysApply: false
---
# MCP Task Management Server Architecture (DDD-Based)

## Overview
This document outlines the **Domain-Driven Design (DDD) architecture** for an MCP (Model Context Protocol) server that provides task management capabilities and automatically generates `.cursor/rules/auto_rule.mdc` files for Cursor IDE integration using **FastMCP 2.0** framework and **YAML-based role system**.

## System Architecture

### 🏗️ DDD Architecture Layers

#### 1. **Domain Layer** (`dhafnck_mcp_main/src/task_mcp/domain/`)
- **Entities**: Core business objects with identity and behavior
  - `Task` - Main task entity with business logic and validation
- **Value Objects**: Immutable objects representing concepts
  - `TaskId` - Unique task identifier
  - `TaskStatus` - Task status with transition rules
  - `Priority` - Task priority levels
- **Domain Events**: Business events that occur in the domain
  - `TaskCreated`, `TaskUpdated`, `TaskRetrieved`, `TaskDeleted`
- **Domain Services**: Business logic that doesn't belong to entities
  - `AutoRuleGenerator` - Interface for rule generation
- **Repositories**: Interfaces for data persistence
  - `TaskRepository` - Abstract interface for task storage
- **Exceptions**: Domain-specific exceptions
  - `TaskNotFoundException`, `InvalidTaskStatusException`

#### 2. **Application Layer** (`dhafnck_mcp_main/src/task_mcp/application/`)
- **Use Cases**: Application-specific business logic
  - `CreateTask`, `GetTask`, `UpdateTask`, `DeleteTask`, `ListTasks`, `SearchTasks`
- **Application Services**: Orchestrate domain operations
  - `TaskApplicationService` - Coordinates task operations and rule generation
- **DTOs (Data Transfer Objects)**: Data contracts for external communication
  - `CreateTaskRequest`, `UpdateTaskRequest`, `ListTasksRequest`, `SearchTasksRequest`
  - `TaskResponse`, `TaskListResponse`, `SearchTasksResponse`

#### 3. **Infrastructure Layer** (`dhafnck_mcp_main/src/task_mcp/infrastructure/`)
- **Repositories**: Concrete implementations of domain repositories
  - `JsonTaskRepository` - JSON file-based task storage
- **External Services**: Integration with external systems
  - `FileAutoRuleGenerator` - Generates auto_rule.mdc files
  - **Legacy Project Analysis System**:
    - `ProjectAnalyzer` - Analyzes project structure and patterns
    - `RoleManager` - Manages YAML-based role system
    - `RulesGenerator` - Generates context-aware rules

#### 4. **Interface Layer** (`dhafnck_mcp_main/src/task_mcp/interface/`)
- **MCP Server**: FastMCP-based server implementation
  - `ddd_mcp_server.py` - Server initialization and configuration
  - `mcp_tools.py` - MCP tool implementations using DDD architecture

### 🛠️ FastMCP Framework Integration

#### Server Implementation
```python
# dhafnck_mcp_main/src/mcp_server.py
from task_mcp.interface.ddd_mcp_server import create_mcp_server

def main():
    mcp = create_mcp_server()  # DDD-based server
    mcp.run()  # FastMCP execution
```

#### Tool Registration
```python
# dhafnck_mcp_main/src/task_mcp/interface/ddd_mcp_server.py
def create_mcp_server() -> FastMCP:
    mcp = FastMCP("Task Management DDD")
    task_tools = MCPTaskTools()
    task_tools.register_tools(mcp)  # Register all 10 MCP tools
    return mcp
```

## 🔧 MCP Tools Architecture (10 Tools)

### Core Task Management Tools
```
create_task(title, description, status, priority, ...)
├── CreateTaskRequest → TaskApplicationService
├── Domain validation via Task entity
├── JsonTaskRepository persistence
└── Returns TaskResponse

get_task(task_id)
├── GetTask use case → TaskApplicationService
├── Triggers TaskRetrieved domain event
├── **AUTO-GENERATES .cursor/rules/auto_rule.mdc**
├── Uses YAML role system integration
└── Returns TaskResponse with auto-rule confirmation

update_task(task_id, updates...)
├── UpdateTaskRequest → TaskApplicationService
├── Domain validation and business rules
├── Triggers TaskUpdated domain events
└── Returns updated TaskResponse

delete_task(task_id)
├── DeleteTask use case
├── Triggers TaskDeleted domain event
├── JsonTaskRepository removal
└── Returns deletion confirmation

list_tasks(filters...)
├── ListTasksRequest with filtering
├── Repository query with pagination
└── Returns TaskListResponse

search_tasks(query, limit)
├── SearchTasksRequest
├── Text search across task fields
└── Returns SearchTasksResponse
```

### Project Management Tools
```
update_project_meta(updates)
├── Updates project metadata
├── JSON storage persistence
└── Returns metadata confirmation

get_project_meta()
├── Retrieves project metadata
├── Includes task statistics
└── Returns project information

get_storage_stats()
├── Analyzes storage usage
├── Task count and size metrics
└── Returns storage statistics

diagnostic_info()
├── Server health and status
├── Configuration validation
└── Returns diagnostic data
```

## 🎯 Auto Rule Generation System

### **YAML-Based Role System** (`dhafnck_mcp_main/yaml-lib/`)
```
yaml-lib/
├── task_planner/
│   ├── job_desc.yaml          # Role definition
│   ├── contexts/              # Context templates
│   ├── rules/                 # Rule definitions
│   └── tools/                 # Tool specifications
├── senior_developer/
├── platform_engineer/
├── qa_engineer/
├── code_reviewer/
├── technical_writer/
├── devops_engineer/
├── security_engineer/
├── context_engineer/
├── metrics_engineer/
├── cache_engineer/
└── cli_engineer/
```

### **Auto Rule Generation Flow**
```
get_task(task_id) → TaskRetrieved Event → FileAutoRuleGenerator
                                              ↓
Role Detection ← Task.assignee → YAML Role Loading ← dhafnck_mcp_main/yaml-lib/
                                              ↓
Project Analysis ← ProjectAnalyzer → Structure Detection
                                              ↓
Rule Generation ← RulesGenerator → Template Processing
                                              ↓
File Output → .cursor/rules/auto_rule.mdc ← Context Integration
```

### **Generated Content Structure**
```markdown
# [Role] - [Phase] Phase
## Current Task Context
- Task ID, title, description, phase, priority, assignee
## Active Roles for This Task
- Primary role and all active roles
## Role & Persona
- Expert persona and primary focus from YAML
## Core Operating Rules
- 25+ detailed rules for code quality and best practices
## Context-Specific Instructions
- Phase-appropriate guidance (planning/coding/testing/review)
## Tools & Output Guidance
- Development best practices and expected outputs
## Project Structure
- Complete project tree view and detected patterns
```

## 📊 Data Flow Architecture

### Task Management Flow (DDD-Based)
```
MCP Client → FastMCP Server → MCPTaskTools → TaskApplicationService
                                                      ↓
Domain Validation ← Task Entity ← Use Case Logic
                                                      ↓
Domain Events → Event Handling → Auto Rule Generation
                                                      ↓
JsonTaskRepository → JSON Storage → File System
                                                      ↓
Response ← DTO Mapping ← Domain Entity ← Repository
```

### Auto Rule Generation Flow
```
TaskRetrieved Event → FileAutoRuleGenerator → ProjectAnalyzer
                                                      ↓
YAML Role System ← RoleManager ← dhafnck_mcp_main/yaml-lib/
                                                      ↓
Context Generation ← RulesGenerator → Template Engine
                                                      ↓
.cursor/rules/auto_rule.mdc ← File Writer ← Validation
```

## 💾 Storage Architecture

### Task Storage (JSON-Based)
```json
{
  "meta": {
    "projectName": "MCP Task Management Server",
    "version": "1.0.0",
    "source": "MCP server for task management and auto rule generation",
    "totalTasksGenerated": 9,
    "transformationType": "MCP_SERVER_DEVELOPMENT",
    "coreFeatures": ["MCP_Protocol_Implementation", "dhafnck_mcp_Tools", ...],
    "last_modified": "ISO_timestamp"
  },
  "tasks": [
    {
      "id": "task_id",
      "title": "Task title",
      "description": "Task description",
      "status": "todo|in_progress|completed",
      "priority": "low|medium|high|critical",
      "details": "Detailed description",
      "estimatedEffort": "time_estimate",
      "assignee": "role_name",
      "assignedRole": {
        "name": "Role Display Name",
        "role": "role_key",
        "persona": "Expert description",
        "primary_focus": "Main responsibilities"
      },
      "labels": ["label1", "label2"],
      "dependencies": ["20250617001", "20250617002"],
      "subtasks": [...],
      "dueDate": "ISO_date",
      "created_at": "ISO_timestamp",
      "updated_at": "ISO_timestamp"
    }
  ]
}
```

### YAML Role Structure
```yaml
# dhafnck_mcp_main/yaml-lib/[role]/job_desc.yaml
name: "Senior Full-Stack Developer"
role: "senior_developer"
persona: "Expert programmer focused on clean, maintainable, and efficient code"
primary_focus: "Code implementation, architecture patterns, and best practices"
responsibilities:
  - "Write clean, maintainable code"
  - "Implement best practices"
  - "Ensure code quality"
```

## 🔒 Security & Error Handling

### Domain-Driven Security
- **Entity Validation**: Business rules enforced at domain level
- **Value Object Immutability**: Prevents invalid state mutations
- **Domain Events**: Audit trail for all business operations
- **Input Sanitization**: At application service boundary

### Error Handling Strategy
```
Interface Layer → Application Layer → Domain Layer
      ↓                    ↓               ↓
MCP Errors ← Application ← Domain Exceptions
            Exceptions
```

## ⚙️ Configuration & Deployment

### Current Deployment Structure
```
dhafnck_mcp_main/
├── src/
│   ├── mcp_server.py              # Main entry point
│   └── task_mcp/                  # DDD architecture
│       ├── domain/                # Business logic
│       ├── application/           # Use cases
│       ├── infrastructure/        # External concerns
│       └── interface/             # MCP integration
├── yaml-lib/                      # Role system
├── start_mcp_server.sh           # Startup script
└── test/                         # Test suite
```

### MCP Server Configuration
```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "/path/to/dhafnck_mcp_main/start_mcp_server.sh",
      "cwd": "/path/to/project"
    }
  }
}
```

### Environment Setup
```bash
# dhafnck_mcp_main/start_mcp_server.sh
#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)/src"
python src/mcp_server.py
```

## 🚀 Performance & Scalability

### DDD Performance Benefits
- **Lazy Loading**: Domain entities loaded on-demand
- **Event-Driven**: Asynchronous rule generation
- **Repository Pattern**: Optimized data access
- **Value Objects**: Immutable and cacheable

### Scalability Considerations
- **Modular Architecture**: Easy to extend with new domains
- **Plugin System**: YAML roles as configuration
- **Stateless Design**: FastMCP server can be replicated
- **JSON Storage**: Simple and reliable for task management scale

## 🔮 Future Extensions

### Planned DDD Enhancements
- **Aggregate Roots**: For complex task hierarchies
- **Domain Services**: Advanced business logic
- **Event Sourcing**: Complete audit trail
- **CQRS**: Separate read/write models

### Integration Possibilities
- **External Task Systems**: Jira, Trello, GitHub Issues
- **AI-Powered Features**: Smart task decomposition
- **Real-time Collaboration**: WebSocket integration
- **Advanced Analytics**: Task completion patterns

## 📋 Current Status

### ✅ Implemented Features
- **DDD Architecture**: Complete 4-layer implementation
- **FastMCP Integration**: 10 MCP tools fully operational
- **YAML Role System**: 12 roles with comprehensive definitions
- **Auto Rule Generation**: Context-aware rule creation
- **JSON Storage**: Reliable task persistence
- **Domain Events**: Business event handling
- **Project Analysis**: Structure and pattern detection

### 🔄 Active Development
- **Enhanced Rule Templates**: More sophisticated generation
- **Performance Optimization**: Caching and lazy loading
- **Extended Role System**: Additional specialized roles
- **Advanced Filtering**: Complex task queries

This DDD-based architecture provides a robust, maintainable, and extensible foundation for the MCP Task Management Server, with clear separation of concerns and strong business logic encapsulation.