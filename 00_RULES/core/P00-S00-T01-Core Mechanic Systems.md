---
description: AI Assistant Core Operating Rules - Runtime variables, session management, tool usage, agent interactions, and orchestration guidelines.
globs: 
alwaysApply: true
task: AI Assistant Core Operating Rules
step: Core
task_id: CORE-001
title: AI Assistant Core Operating Rules
previous_task: N/A
next_task: N/A
version: 0.0.1
agent: "@uber-orchestrator-agent"
orchestrator: "@uber-orchestrator-agent"
---
This document outlines the core operating rules for the AI Assistant, designed for clear and efficient processing by AI agents. These rules govern runtime variables, session management, tool usage, agent interactions, file access, and overall AI assistant orchestration.


> **📋 For Detailed MCP System Rules**: See [MCP Task Management: Best Practices Guide.mdc](mdc:.cursor/rules/MCP Task Management: Best Practices Guide.mdc) for comprehensive MCP system architecture, workflows, task management, agent coordination, and context management guidelines.

### 🧠 **AI Assistant Core Operating Rules**

#### 1. **Runtime Variables Management**
*   **Variables**: Runtime variables are defined in `.cursor/settings.json` and managed automatically by the system.
*   **Path Reference**: Refer to `@need-update-this-file-if-change-project-tree.mdc` for path information.

#### 2. **Session Initialization**
At the beginning of each new session, perform the following steps:
1.  **Load MCP context** using `MCP tools`.
2.  **Read the core rule file**: `MCP Task Management: Best Practices Guide.mdc`.


#### 3. **During Chat Session**

##### A. **Tool Usage**
*   **Tool Call Tracking**: **Tool usage is automatically tracked** according to settings configuration.
*   **Context Sync**: **Automatic context synchronization** occurs based on configured thresholds via `manage_context()`.

##### B. **Terminal Commands**
*   **Timeout Protection**: All terminal commands **must be run with timeout protection wrapper**.
*   **Force Quit**: If no result is obtained after `20` seconds, **force quit the command**.
*   **Result Display**: **Always show the result if any**.

##### C. **MCP Agent Tool Calls**
**Use the following sequence for each agent interaction**:
*   `"Call Agent..."` → **`call_agent()`**.
*   `"Retrieve Knowledge..."` → (gather all relevant information).
*   `"Switch Agent Capacity..."` → (end call).
*   `"Using dhafnck Tool..."` → (for calls to tools that are not `call_agent()`).

#### 4. **General Context Management Principles**
*   **Context Updates**: **Always check and update context** from `.cursor/rules/auto_rule.mdc`.
*   **Context Sync**: **Use `manage_context()` for context updates relative to tasks**.
*   **Role Alignment**: **Align the AI's role and context automatically with the current task or subtask**.
*   **Progress Logging**: **Regularly log progress and insights during implementation**.
*   **Session Continuity**: **Update next steps to maintain session continuity** and guide subsequent actions.

#### 5. **File Access Rules**
*   **Restricted Access**: **NEVER directly access files within `.cursor/rules/tasks/**/*`**.
*   **MCP Server Usage**: **Use the `dhafnck_mcp` MCP server to manage all tasks and data**.
*   **Manual Access Exception**: Only access these files manually if the **user explicitly requests it**.
*   **Rule File Behavior**: The file `.cursor/rules/auto_rule.mdc` **CAN be READ by the AI (✅)** but **CANNOT be EDITED by the AI (❌)**.

#### 6. **Agent Switching Triggers**
*   **Trigger Events**: Automatic role switching is **triggered by**:
    1.  `manage_task` with `action="get"` (retrieving task details).
    2.  `manage_task` with `action="next"` (getting the next recommended task).
    3.  **Directly using the `call_agent` tool** (manual or system-invoked).
*   **Immediate Switching**: When `call_agent` is used, the **AI immediately switches its role and context** to the specified agent.
*   **Role Adaptation**: The AI adopts the specialized agent's expertise, knowledge base, and behavioral patterns.

> **⚠️ For Complete MCP System Details**: Refer to [MCP Task Management: Best Practices Guide.mdc](mdc:.cursor/rules/MCP Task Management: Best Practices Guide.mdc) for detailed information on:
> - Task ID formats and management rules
> - Agent assignment and coordination specifics  
> - Context management workflows and dot notation
> - Project structure and deployment architecture
> - Complete MCP tool usage guidelines
> - YAML configuration requirements

These rules provide the foundational operating principles for AI Assistant behavior, with detailed MCP system operations covered in the comprehensive MCP Task Management guide.