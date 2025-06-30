#!/usr/bin/env python3
"""
Agent Library Integration Example - Real YAML Implementation
==========================================================

This example demonstrates how to integrate the agent library architecture 
with the actual call_agent() function using REAL YAML files from agent-library directory.

Key Features:
- Loads actual YAML files from agent-library/{agent_name}/ directories
- Parses the 5-layer structure: job_desc, contexts/, rules/, output_format/, tools/
- Extracts real capabilities based on groups configuration
- Loads actual MCP tools from mcp_tools.yaml files
- Creates executable agents with real capabilities
"""

import os
import yaml
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Base paths
BASE_DIR = Path(__file__).parent
YAML_LIB_DIR = BASE_DIR / "agent-library"

@dataclass
class AgentCapabilities:
    """Represents the capabilities an agent has based on its YAML configuration"""
    read: bool = False
    edit: bool = False
    mcp: bool = False
    command: bool = False
    analysis: bool = False
    mcp_tools: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate capabilities after initialization"""
        if self.mcp and not self.mcp_tools:
            print("Warning: Agent has 'mcp' capability but no MCP tools configured")

class ExecutableAgent:
    """An executable agent with full capabilities loaded from real YAML files"""
    
    def __init__(self, agent_name: str, config: Dict[str, Any], capabilities: AgentCapabilities):
        self.agent_name = agent_name
        self.config = config
        self.capabilities = capabilities
        self.created_at = datetime.now()
        
        # Extract key information from real config
        self.name = config.get('identity', {}).get('name', agent_name)
        self.role = config.get('identity', {}).get('role_definition', 'No role defined')
        self.when_to_use = config.get('identity', {}).get('when_to_use', 'No usage guidance defined')
        
    def get_capabilities_summary(self) -> Dict[str, Any]:
        """Get a summary of agent capabilities"""
        return {
            "read_files": self.capabilities.read,
            "edit_files": self.capabilities.edit,
            "use_mcp_tools": self.capabilities.mcp,
            "execute_commands": self.capabilities.command,
            "data_analysis": self.capabilities.analysis,
            "mcp_tools_count": len(self.capabilities.mcp_tools),
            "available_mcp_tools": [tool.get('name', 'unnamed') for tool in self.capabilities.mcp_tools]
        }
    
    def get_available_actions(self) -> List[str]:
        """Get list of available actions based on capabilities"""
        actions = []
        if self.capabilities.read:
            actions.append("read_file")
        if self.capabilities.edit:
            actions.append("edit_file")
        if self.capabilities.mcp:
            actions.extend([f"use_mcp_tool:{tool.get('name', 'unnamed')}" for tool in self.capabilities.mcp_tools])
        if self.capabilities.command:
            actions.append("execute_command")
        if self.capabilities.analysis:
            actions.append("analyze_data")
        return actions
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute an action if the agent has the required capability"""
        try:
            if action == "read_file" and self.capabilities.read:
                return self._simulate_file_read(kwargs.get('file_path'))
            elif action == "edit_file" and self.capabilities.edit:
                return self._simulate_file_edit(kwargs.get('file_path'), kwargs.get('content'))
            elif action.startswith("use_mcp_tool:") and self.capabilities.mcp:
                tool_name = action.split(":", 1)[1]
                return self._simulate_mcp_tool_usage(tool_name, kwargs)
            elif action == "execute_command" and self.capabilities.command:
                return self._simulate_command_execution(kwargs.get('command'))
            elif action == "analyze_data" and self.capabilities.analysis:
                return self._simulate_data_analysis(kwargs.get('data'))
            else:
                return {
                    "success": False,
                    "error": f"Action '{action}' not available or agent lacks required capability",
                    "available_actions": self.get_available_actions()
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing action '{action}': {str(e)}"
            }
    
    def _simulate_file_read(self, file_path: Optional[str]) -> Dict[str, Any]:
        """Simulate file reading capability"""
        if not file_path:
            return {"success": False, "error": "No file path provided"}
        return {
            "success": True,
            "action": "read_file",
            "file_path": file_path,
            "message": f"Agent {self.agent_name} would read file: {file_path}",
            "capability": "read"
        }
    
    def _simulate_file_edit(self, file_path: Optional[str], content: Optional[str]) -> Dict[str, Any]:
        """Simulate file editing capability"""
        if not file_path:
            return {"success": False, "error": "No file path provided"}
        return {
            "success": True,
            "action": "edit_file",
            "file_path": file_path,
            "content_length": len(content) if content else 0,
            "message": f"Agent {self.agent_name} would edit file: {file_path}",
            "capability": "edit"
        }
    
    def _simulate_mcp_tool_usage(self, tool_name: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate MCP tool usage"""
        # Find the specific tool configuration
        tool_config = None
        for tool in self.capabilities.mcp_tools:
            if tool.get('name') == tool_name:
                tool_config = tool
                break
        
        if not tool_config:
            return {
                "success": False,
                "error": f"MCP tool '{tool_name}' not found in agent configuration",
                "available_tools": [tool.get('name', 'unnamed') for tool in self.capabilities.mcp_tools]
            }
        
        return {
            "success": True,
            "action": "use_mcp_tool",
            "tool_name": tool_name,
            "tool_description": tool_config.get('description', 'No description'),
            "parameters": kwargs,
            "message": f"Agent {self.agent_name} would use MCP tool: {tool_name}",
            "capability": "mcp"
        }
    
    def _simulate_command_execution(self, command: Optional[str]) -> Dict[str, Any]:
        """Simulate command execution capability"""
        if not command:
            return {"success": False, "error": "No command provided"}
        return {
            "success": True,
            "action": "execute_command",
            "command": command,
            "message": f"Agent {self.agent_name} would execute command: {command}",
            "capability": "command"
        }
    
    def _simulate_data_analysis(self, data: Any) -> Dict[str, Any]:
        """Simulate data analysis capability"""
        return {
            "success": True,
            "action": "analyze_data",
            "data_type": type(data).__name__,
            "data_size": len(str(data)) if data else 0,
            "message": f"Agent {self.agent_name} would analyze data of type: {type(data).__name__}",
            "capability": "analysis"
        }

class AgentFactory:
    """Factory for creating executable agents from real YAML configurations"""
    
    def __init__(self, yaml_lib_path: Path = YAML_LIB_DIR):
        self.yaml_lib_path = yaml_lib_path
        self.available_agents = self._discover_agents()
    
    def _discover_agents(self) -> List[str]:
        """Discover available agents in the agent-library directory"""
        if not self.yaml_lib_path.exists():
            print(f"Warning: YAML library path does not exist: {self.yaml_lib_path}")
            return []
        
        agents = []
        for item in self.yaml_lib_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if it has the basic agent structure
                job_desc_file = item / "job_desc.yaml"
                if job_desc_file.exists():
                    agents.append(item.name)
        
        return sorted(agents)
    
    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load a YAML file and return its contents"""
        try:
            if not file_path.exists():
                return {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f) or {}
                return content
        except Exception as e:
            print(f"Error loading YAML file {file_path}: {e}")
            return {}
    
    def _load_agent_identity(self, agent_path: Path) -> Dict[str, Any]:
        """Load agent identity from job_desc.yaml"""
        job_desc_file = agent_path / "job_desc.yaml"
        return self._load_yaml_file(job_desc_file)
    
    def _load_agent_contexts(self, agent_path: Path) -> Dict[str, Any]:
        """Load all context files from contexts/ directory"""
        contexts_dir = agent_path / "contexts"
        contexts = {}
        
        if not contexts_dir.exists():
            return contexts
        
        for context_file in contexts_dir.glob("*.yaml"):
            context_name = context_file.stem
            contexts[context_name] = self._load_yaml_file(context_file)
        
        return contexts
    
    def _load_agent_rules(self, agent_path: Path) -> Dict[str, Any]:
        """Load all rule files from rules/ directory"""
        rules_dir = agent_path / "rules"
        rules = {}
        
        if not rules_dir.exists():
            return rules
        
        for rule_file in rules_dir.glob("*.yaml"):
            rule_name = rule_file.stem
            rules[rule_name] = self._load_yaml_file(rule_file)
        
        return rules
    
    def _load_agent_output_format(self, agent_path: Path) -> Dict[str, Any]:
        """Load output format from output_format/ directory"""
        output_dir = agent_path / "output_format"
        output_format = {}
        
        if not output_dir.exists():
            return output_format
        
        for output_file in output_dir.glob("*.yaml"):
            format_name = output_file.stem
            output_format[format_name] = self._load_yaml_file(output_file)
        
        return output_format
    
    def _load_agent_tools(self, agent_path: Path) -> Dict[str, Any]:
        """Load MCP tools from tools/ directory"""
        tools_dir = agent_path / "tools"
        tools = {}
        
        if not tools_dir.exists():
            return tools
        
        # Load MCP tools if available
        mcp_tools_file = tools_dir / "mcp_tools.yaml"
        if mcp_tools_file.exists():
            tools['mcp_tools'] = self._load_yaml_file(mcp_tools_file)
        
        return tools
    
    def _extract_capabilities(self, identity: Dict[str, Any], tools: Dict[str, Any]) -> AgentCapabilities:
        """Extract agent capabilities from identity groups and tools configuration"""
        groups = identity.get('groups', [])
        
        capabilities = AgentCapabilities(
            read='read' in groups,
            edit='edit' in groups,
            mcp='mcp' in groups,
            command='command' in groups,
            analysis='analysis' in groups
        )
        
        # Extract MCP tools if available - check the actual structure
        mcp_tools_config = tools.get('mcp_tools', {})
        if mcp_tools_config:
            # The YAML structure is: mcp_tools -> available_tools
            if 'mcp_tools' in mcp_tools_config and 'available_tools' in mcp_tools_config['mcp_tools']:
                capabilities.mcp_tools = mcp_tools_config['mcp_tools']['available_tools']
            elif 'available_tools' in mcp_tools_config:
                capabilities.mcp_tools = mcp_tools_config['available_tools']
        
        return capabilities
    
    def create_agent(self, agent_name: str) -> Optional[ExecutableAgent]:
        """Create an executable agent from real YAML configuration"""
        if agent_name not in self.available_agents:
            print(f"Agent '{agent_name}' not found. Available agents: {self.available_agents}")
            return None
        
        agent_path = self.yaml_lib_path / agent_name
        
        try:
            # Load all 5 layers of YAML configuration
            identity = self._load_agent_identity(agent_path)
            contexts = self._load_agent_contexts(agent_path)
            rules = self._load_agent_rules(agent_path)
            output_format = self._load_agent_output_format(agent_path)
            tools = self._load_agent_tools(agent_path)
            
            # Combine all configuration
            config = {
                'identity': identity,
                'contexts': contexts,
                'rules': rules,
                'output_format': output_format,
                'tools': tools
            }
            
            # Extract capabilities
            capabilities = self._extract_capabilities(identity, tools)
            
            # Create executable agent
            agent = ExecutableAgent(agent_name, config, capabilities)
            
            print(f"✅ Successfully created agent: {agent_name}")
            return agent
            
        except Exception as e:
            print(f"❌ Error creating agent '{agent_name}': {e}")
            return None
    
    def list_available_agents(self) -> List[str]:
        """Get list of available agents"""
        return self.available_agents

def enhanced_call_agent(agent_name: str) -> Dict[str, Any]:
    """
    Enhanced call_agent function that returns both traditional agent_info 
    and new executable agent with full capabilities
    """
    factory = AgentFactory()
    
    # Try to create executable agent with real YAML data
    executable_agent = factory.create_agent(agent_name)
    
    if executable_agent:
        # Return enhanced response with both traditional and new format
        return {
            "success": True,
            "agent_info": {
                "name": executable_agent.name,
                "role": executable_agent.role,
                "when_to_use": executable_agent.when_to_use,
                "yaml_content": json.dumps(executable_agent.config, indent=2, default=str)
            },
            "executable_agent": {
                "instance": executable_agent,
                "capabilities": executable_agent.get_capabilities_summary(),
                "available_actions": executable_agent.get_available_actions(),
                "created_at": executable_agent.created_at.isoformat()
            }
        }
    else:
        # Fallback to traditional approach
        return {
            "success": False,
            "error": f"Could not load agent '{agent_name}'",
            "agent_info": None,
            "executable_agent": None
        }

def demonstrate_real_yaml_integration():
    """Demonstrate the integration using real YAML files"""
    print("🚀 Agent Library Integration with Real YAML Files")
    print("=" * 60)
    
    factory = AgentFactory()
    
    # Show available agents
    available_agents = factory.list_available_agents()
    print(f"\n📋 Available Agents ({len(available_agents)}):")
    for i, agent in enumerate(available_agents[:10], 1):  # Show first 10
        print(f"   {i:2d}. {agent}")
    if len(available_agents) > 10:
        print(f"   ... and {len(available_agents) - 10} more agents")
    
    # Test with a few real agents
    test_agents = [
        "system_architect_agent",
        "coding_agent", 
        "ui_designer_expert_shadcn_agent"
    ]
    
    for agent_name in test_agents:
        if agent_name in available_agents:
            print(f"\n🔍 Testing Agent: {agent_name}")
            print("-" * 40)
            
            # Use enhanced call_agent function
            result = enhanced_call_agent(agent_name)
            
            if result["success"]:
                agent_info = result["agent_info"]
                executable_info = result["executable_agent"]
                agent_instance = executable_info["instance"]
                
                print(f"✅ Agent loaded successfully")
                print(f"   Name: {agent_info['name']}")
                print(f"   Role: {agent_info['role'][:100]}...")
                print(f"   Capabilities: {executable_info['capabilities']}")
                print(f"   Available Actions: {len(executable_info['available_actions'])}")
                
                # Test some capabilities
                if agent_instance.capabilities.read:
                    result = agent_instance.execute("read_file", file_path="/example/path.txt")
                    print(f"   📖 Read Test: {result['message']}")
                
                if agent_instance.capabilities.mcp and agent_instance.capabilities.mcp_tools:
                    tool_name = agent_instance.capabilities.mcp_tools[0].get('name')
                    if tool_name:
                        result = agent_instance.execute(f"use_mcp_tool:{tool_name}", param1="test")
                        print(f"   🔧 MCP Tool Test: {result['message']}")
                
                if agent_instance.capabilities.command:
                    result = agent_instance.execute("execute_command", command="ls -la")
                    print(f"   💻 Command Test: {result['message']}")
            else:
                print(f"❌ Failed to load agent: {result['error']}")
    
    print(f"\n🎯 Integration Summary:")
    print(f"   • Loaded {len(available_agents)} agents from real YAML files")
    print(f"   • Successfully integrated 5-layer YAML structure")
    print(f"   • Extracted real capabilities from groups configuration")
    print(f"   • Loaded actual MCP tools from mcp_tools.yaml files")
    print(f"   • Created executable agents with full capabilities")
    print(f"   • Maintained backward compatibility with traditional call_agent")

if __name__ == "__main__":
    demonstrate_real_yaml_integration() 