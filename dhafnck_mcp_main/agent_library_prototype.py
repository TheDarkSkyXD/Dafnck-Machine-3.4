#!/usr/bin/env python3
"""
Agent Library Prototype

This prototype demonstrates the core concepts of the agent library architecture
based on the analysis of ui_designer_expert_shadcn_agent.

Author: AI System Architect
Version: 1.0.0
Date: 2025-01-27
"""

import yaml
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Agent configuration data structure"""
    name: str
    slug: str
    role_definition: str
    when_to_use: str
    groups: List[str]
    version: str = "1.0.0"
    author: str = "Unknown"
    tags: List[str] = field(default_factory=list)

class BaseAgent(ABC):
    """Base class for all agents providing core functionality"""
    
    def __init__(self, config: 'AgentConfig'):
        self.config = config
        logger.info(f"Initialized agent: {self.config.name}")
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return self.config.groups
    
    def has_capability(self, capability: str) -> bool:
        """Check if agent has specific capability"""
        return capability in self.config.groups
    
    @abstractmethod
    def execute(self, input_data: Dict) -> Dict:
        """Execute agent with given input"""
        pass
    
    def get_documentation(self) -> Dict:
        """Generate agent documentation"""
        return {
            "name": self.config.name,
            "slug": self.config.slug,
            "role": self.config.role_definition,
            "when_to_use": self.config.when_to_use,
            "capabilities": self.config.groups,
            "version": self.config.version,
            "author": self.config.author
        }

class SimpleAgent(BaseAgent):
    """Simple agent implementation for demonstration"""
    
    def execute(self, input_data: Dict) -> Dict:
        """Execute agent with given input"""
        logger.info(f"Executing {self.config.name} with input: {input_data}")
        
        action = input_data.get('action', 'default')
        
        if action == 'analyze':
            return self._analyze(input_data)
        elif action == 'process':
            return self._process(input_data)
        else:
            return self._default_action(input_data)
    
    def _analyze(self, input_data: Dict) -> Dict:
        """Perform analysis action"""
        return {
            "action": "analyze",
            "agent": self.config.name,
            "result": f"Analysis completed by {self.config.name}",
            "data": input_data.get('data', {}),
            "capabilities_used": [cap for cap in self.config.groups if cap in ['analysis', 'read']]
        }
    
    def _process(self, input_data: Dict) -> Dict:
        """Perform processing action"""
        return {
            "action": "process",
            "agent": self.config.name,
            "result": f"Processing completed by {self.config.name}",
            "data": input_data.get('data', {}),
            "capabilities_used": [cap for cap in self.config.groups if cap in ['edit', 'read']]
        }
    
    def _default_action(self, input_data: Dict) -> Dict:
        """Default action"""
        return {
            "action": "default",
            "agent": self.config.name,
            "result": f"Default action executed by {self.config.name}",
            "input": input_data,
            "capabilities": self.config.groups
        }

class AgentBuilder:
    """Utility class for creating new agents"""
    
    def create_from_template(self, template: str, name: str, config: Dict) -> SimpleAgent:
        """Create agent from template"""
        
        # Create agent configuration
        agent_config = AgentConfig(
            name=config.get('name', name),
            slug=config.get('slug', name.lower().replace(' ', '-')),
            role_definition=config.get('role', ''),
            when_to_use=config.get('when_to_use', ''),
            groups=config.get('capabilities', []),
            version=config.get('version', '1.0.0'),
            author=config.get('author', 'Agent Builder'),
            tags=config.get('tags', [])
        )
        
        # Add template-specific capabilities
        if template == 'mcp' and 'mcp' not in agent_config.groups:
            agent_config.groups.append('mcp')
        elif template == 'specialized':
            default_capabilities = ['read', 'edit', 'mcp', 'analysis']
            for cap in default_capabilities:
                if cap not in agent_config.groups:
                    agent_config.groups.append(cap)
        
        return SimpleAgent(agent_config)

class AgentRegistry:
    """Central registry for agent management"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        logger.info("Initialized AgentRegistry")
    
    def register_agent(self, agent: BaseAgent) -> bool:
        """Register new agent"""
        if agent.config.slug in self.agents:
            logger.warning(f"Agent {agent.config.slug} already registered")
            return False
        
        self.agents[agent.config.slug] = agent
        logger.info(f"Registered agent: {agent.config.name} ({agent.config.slug})")
        return True
    
    def get_agent(self, slug: str) -> Optional[BaseAgent]:
        """Retrieve agent by slug"""
        return self.agents.get(slug)
    
    def list_agents(self) -> List[Dict]:
        """List all registered agents"""
        return [agent.get_documentation() for agent in self.agents.values()]
    
    def discover_agents(self, criteria: Dict) -> List[BaseAgent]:
        """Discover agents by criteria"""
        matching_agents = []
        
        for agent in self.agents.values():
            match = True
            
            # Check capability criteria
            if 'capability' in criteria:
                if not agent.has_capability(criteria['capability']):
                    match = False
            
            # Check tag criteria
            if 'tag' in criteria and match:
                if criteria['tag'] not in agent.config.tags:
                    match = False
            
            if match:
                matching_agents.append(agent)
        
        return matching_agents
    
    def get_statistics(self) -> Dict:
        """Get registry statistics"""
        total_agents = len(self.agents)
        mcp_agents = len([a for a in self.agents.values() if a.has_capability('mcp')])
        analysis_agents = len([a for a in self.agents.values() if a.has_capability('analysis')])
        
        return {
            "total_agents": total_agents,
            "mcp_enabled_agents": mcp_agents,
            "analysis_agents": analysis_agents,
            "agents_by_capability": self._get_capability_stats()
        }
    
    def _get_capability_stats(self) -> Dict[str, int]:
        """Get statistics by capability"""
        stats = {}
        for agent in self.agents.values():
            for capability in agent.get_capabilities():
                stats[capability] = stats.get(capability, 0) + 1
        return stats

def demonstrate_agent_library():
    """Demonstrate the agent library functionality"""
    print("🚀 Agent Library Prototype Demonstration")
    print("=" * 50)
    
    # Initialize components
    builder = AgentBuilder()
    registry = AgentRegistry()
    
    # Create different types of agents
    print("\n📝 Creating Agents...")
    
    # Basic agent
    text_agent = builder.create_from_template(
        template='basic',
        name='text_processor',
        config={
            'role': 'Process and analyze text content',
            'capabilities': ['read', 'analysis'],
            'when_to_use': 'For text processing and analysis tasks'
        }
    )
    registry.register_agent(text_agent)
    
    # MCP-enabled agent
    doc_agent = builder.create_from_template(
        template='mcp',
        name='document_manager',
        config={
            'role': 'Manage documents and files',
            'capabilities': ['read', 'edit'],
            'when_to_use': 'For document management tasks',
            'tools': ['manage_document', 'manage_context']
        }
    )
    registry.register_agent(doc_agent)
    
    # Specialized agent
    data_agent = builder.create_from_template(
        template='specialized',
        name='data_analyst',
        config={
            'role': 'Analyze data and generate insights',
            'when_to_use': 'For data analysis and visualization tasks',
            'tags': ['data', 'analysis', 'visualization']
        }
    )
    registry.register_agent(data_agent)
    
    # Display registry statistics
    print("\n📊 Registry Statistics:")
    stats = registry.get_statistics()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")
    
    # Demonstrate agent discovery
    print("\n🔍 Agent Discovery:")
    mcp_agents = registry.discover_agents({'capability': 'mcp'})
    print(f"  MCP-enabled agents: {[a.config.name for a in mcp_agents]}")
    
    analysis_agents = registry.discover_agents({'capability': 'analysis'})
    print(f"  Analysis agents: {[a.config.name for a in analysis_agents]}")
    
    # Demonstrate agent execution
    print("\n⚡ Agent Execution:")
    
    # Execute text processing
    result = text_agent.execute({
        'action': 'analyze',
        'data': {'text': 'Sample text for analysis'}
    })
    print(f"  Text Agent Result: {result['result']}")
    
    # Execute document management
    result = doc_agent.execute({
        'action': 'process',
        'data': {'documents': ['doc1.txt', 'doc2.txt']}
    })
    print(f"  Document Agent Result: {result['result']}")
    
    # Execute data analysis
    result = data_agent.execute({
        'action': 'analyze',
        'data': {'dataset': 'sales_data.csv', 'metrics': ['revenue', 'growth']}
    })
    print(f"  Data Agent Result: {result['result']}")
    
    # Display agent documentation
    print("\n�� Agent Documentation:")
    for agent_doc in registry.list_agents():
        print(f"  Agent: {agent_doc['name']}")
        print(f"    Role: {agent_doc['role']}")
        print(f"    Capabilities: {', '.join(agent_doc['capabilities'])}")
        print()
    
    print("✅ Agent Library Demonstration Complete!")

if __name__ == "__main__":
    demonstrate_agent_library()
