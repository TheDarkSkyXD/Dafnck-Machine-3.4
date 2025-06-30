"""File-based Auto Rule Generator Implementation"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging
import sys
from datetime import datetime

from ...domain import Task, AutoRuleGenerator
from .legacy.rules_generator import RulesGenerator
from ...domain.enums.agent_roles import get_supported_roles as get_all_supported_roles
from fastmcp.tools.tool_path import find_project_root


def _get_project_root() -> Path:
    """Get project root directory by searching for the .git folder."""
    current_path = Path(__file__).resolve()
    # Iterate upwards from the current file's location
    while current_path != current_path.parent:
        if (current_path / ".git").is_dir():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError("Could not determine project root. Searched for '.git' directory.")


class FileAutoRuleGenerator(AutoRuleGenerator):
    """File-based implementation of AutoRuleGenerator
    
    The output path can be set by:
    1. Passing output_path to the constructor
    2. Setting the AUTO_RULE_PATH environment variable
    3. Defaults to .cursor/rules/auto_rule.mdc under the project root
    """
    
    def __init__(self, output_path: Optional[str] = None):
        # Only call find_project_root here, not at module/global scope
        project_root = find_project_root()

        def resolve_path(path):
            p = Path(path)
            return str(p if p.is_absolute() else (project_root / p))

        env_path = os.environ.get("AUTO_RULE_PATH")
        if output_path:
            self._output_path = resolve_path(output_path)
        elif env_path:
            self._output_path = resolve_path(env_path)
        else:
            self._output_path = str(project_root / ".cursor" / "rules" / "auto_rule.mdc")
        
        # Initialize RulesGenerator with the agent-library directory
        yaml_lib_dir = project_root / "cursor_agent" / "agent-library"
        self._rules_generator = RulesGenerator(yaml_lib_dir)
        self._ensure_output_dir()
        
        print(f"DEBUG: FileAutoRuleGenerator initialized. Output path set to: {self._output_path}")
    
    @property
    def output_path(self) -> str:
        """Get the output path for the auto rule file"""
        return self._output_path
    
    def _ensure_output_dir(self):
        """Ensure the output directory exists"""
        try:
            output_dir = os.path.dirname(self._output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
        except PermissionError:
            import tempfile
            self._output_path = os.path.join(tempfile.gettempdir(), f"auto_rule_{os.getpid()}.mdc")
    
    def generate_rules_for_task(self, task: Task, force_full_generation: bool = False) -> bool:
        """Generate auto rules for the given task."""
        if not force_full_generation:
            logging.info("Using simple rules generation (force_full_generation=False)")
            self._generate_simple_rules(task)
            return True
        
        # If we are here, it's either not a test env or full generation is forced
        logging.info("Attempting to generate comprehensive rules.")
        
        # Get the project root directory
        project_root = _get_project_root()
        logging.info(f"Project root found at: {project_root}")

        # Import the migrated rule generation system
        from .legacy.rules_generator import RulesGenerator
        from .legacy.role_manager import RoleManager
        from .legacy.project_analyzer import ProjectAnalyzer
        
        logging.info("Legacy modules imported successfully.")
        
        # Convert domain task to the format expected by the original system
        task_dict = task.to_dict()
        
        # Create a simplified task context that matches what the original system expects
        # Based on the TaskContext class in models.py, it expects these fields:
        # id, title, description, requirements, current_phase, assigned_raaoles, primary_role, context_data, created_at, updated_at, progress
        
        # Map task status to phase
        status_to_phase_map = {
            "todo": "planning",
            "in_progress": "coding", 
            "testing": "testing",
            "review": "review",
            "completed": "completed",
            "cancelled": "completed",
            "blocked": "planning"
        }
        
        current_phase = status_to_phase_map.get(task_dict["status"], "coding")
        # Get primary assignee from assignees list (first one) or use default
        assignees = task_dict.get("assignees", ["senior_developer"])
        primary_assignee = assignees[0] if assignees else "senior_developer"
        assigned_roles = [primary_assignee]
        
        # Create a mock TaskContext-like object with the required fields
        class SimpleTaskContext:
            def __init__(self):
                self.id = str(task_dict["id"])
                self.title = task_dict["title"]
                self.description = task_dict["description"]
                self.requirements = [task_dict.get("details", "")]
                self.current_phase = current_phase
                self.assigned_roles = assigned_roles
                self.primary_role = assigned_roles[0]
                self.context_data = {
                    "priority": task_dict["priority"],
                    "estimated_effort": task_dict.get("estimatedEffort", ""),
                    "labels": task_dict.get("labels", []),
                    "subtasks": task_dict.get("subtasks", [])
                }
                self.created_at = datetime.now()
                self.updated_at = datetime.now()
                self.progress = None
        
        task_context = SimpleTaskContext()
        logging.info(f"Task context created for task ID: {task_context.id}")
        
        # Load role information using the original role manager
        lib_dir = project_root / "dhafnck_mcp_main" / "agent-library"
        role_manager = RoleManager(lib_dir)
        assignee = primary_assignee
        
        # Load the role data from YAML files
        loaded_roles = role_manager.load_specific_roles([assignee])
        
        # Get the loaded role or create a fallback
        if loaded_roles and assignee in loaded_roles:
            agent_role = loaded_roles[assignee]
            logging.info(f"Loaded agent role '{assignee}' successfully.")
        else:
            logging.warning(f"Could not load role '{assignee}', creating fallback.")
            # Fallback: try to get role by mapping
            role_name = role_manager.get_role_from_assignee(assignee)
            if role_name and role_name in loaded_roles:
                agent_role = loaded_roles[role_name]
                logging.info(f"Found role by mapping: '{role_name}'")
            else:
                logging.warning(f"Role mapping for '{assignee}' failed, creating basic role.")
                # Create a basic role as fallback
                class SimpleAgentRole:
                    def __init__(self, name):
                        self.name = name
                        self.persona = "Expert developer"
                        self.persona_icon = "❓"
                        self.primary_focus = "Implementation"
                        self.rules = ["Write clean, maintainable code", "Follow best practices"]
                        self.context_instructions = ["Focus on code quality"]
                        self.tools_guidance = ["Use appropriate tools"]
                        self.output_format = "Complete implementation"
                
                agent_role = SimpleAgentRole(assignee)
        
        # Analyze project using the original project analyzer
        project_analyzer = ProjectAnalyzer(project_root)
        project_context = project_analyzer.get_context_for_agent_integration(current_phase)
        logging.info("Project context analyzed.")
        
        # Generate rules using the original rules generator
        rules_generator = RulesGenerator(project_root / "dhafnck_mcp_main" / "agent-library")
        generated_rules = rules_generator.build_rules_content(task_context, agent_role, project_context)
        
        # Write to file
        with open(self._output_path, 'w', encoding='utf-8') as f:
            f.write(generated_rules)
        
        logging.info(f"Successfully generated comprehensive rules for task {task_dict['id']}")
        return True
    
    def _generate_simple_rules(self, task: Task):
        """Generate a simplified version of auto rules for testing"""
        from datetime import datetime
        # Get primary assignee
        assignee = task.get_primary_assignee()
        if not assignee:
            assignee = "default_agent"
        
        # Ensure assignee is a string before calling startswith()
        assignee_str = str(assignee)
        
        # Remove '@' prefix if present
        if assignee_str.startswith("@"):
            assignee_str = assignee_str[1:]

        # Convert task to dict
        task_dict = task.to_dict()
        
        # Create a basic rule set
        content = f"""
### DO NOT EDIT - THIS FILE IS AUTOMATICALLY GENERATED ###
# Last generated: {datetime.now().isoformat()}

# --- Simplified Rules for Test Environment ---

### TASK CONTEXT ###
- **ID**: {task_dict.get('id', 'N/A')}
- **Title**: {task_dict.get('title', 'N/A')}
- **Description**: {task_dict.get('description', 'N/A')}
- **Priority**: {str(task_dict.get('priority', 'N/A')).upper()}
- **Labels**: {', '.join(task_dict.get('labels', []))}

### ROLE: {assignee_str.upper()} ###
- This is a simplified role for testing purposes.

### OPERATING RULES ###
1.  Focus on completing the task as described.
2.  Use mocks and stubs for external dependencies.
3.  Write clear and concise code.

### --- END OF GENERATED RULES --- ###
"""
        try:
            with open(self._output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except PermissionError:
            logging.warning(f"Permission denied for {self._output_path}. Falling back to temp directory.")
            try:
                import tempfile
                fallback_path = os.path.join(tempfile.gettempdir(), f"auto_rule_task_{task.id.value}_{os.getpid()}.mdc")
                with open(fallback_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logging.info(f"Wrote to fallback file: {fallback_path}")
            except Exception as e:
                logging.error(f"Could not write to fallback file: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while writing simple rules: {e}")
    
    def validate_task_data(self, task_data: Dict[str, Any]) -> bool:
        """Validate that task data is sufficient for rule generation"""
        # This can be expanded with more sophisticated validation logic
        required_fields = ["id", "title", "description", "status", "priority"]
        return all(field in task_data for field in required_fields)
    
    def get_supported_roles(self) -> list[str]:
        """Get a list of all supported agent roles"""
        try:
            # Use the enum helper function to get all roles
            return get_all_supported_roles()
        except Exception as e:
            logging.error(f"Failed to get supported roles: {e}")
            return []
    
    def get_role_details(self, role: str) -> Dict[str, Any]:
        """Get details for a specific role"""
        return self._rules_generator.get_role_details(role)

    def generate(self, task: "Task", project_context: Dict[str, Any], agent_role: Any) -> str:
        """Generate rules content (for compatibility with older interfaces)"""
        
        # Create a simplified task context from the domain task
        task_context = self._map_task_to_context(task)
        
        return self._rules_generator.build_rules_content(
            task=task_context,
            role=agent_role,
            project_context=project_context
        )

    def _map_task_to_context(self, task: "Task") -> Any:
        """Map the domain Task entity to a simplified context object for RulesGenerator"""
        
        class SimpleTaskContext:
            def __init__(self, t):
                self.id = str(t.id)
                self.title = t.title
                self.description = t.description
                self.requirements = [t.details or ""]
                self.current_phase = t.status.value
                self.assigned_roles = t.assignees
                self.primary_role = t.assignees[0] if t.assignees else "senior_developer"
                self.context_data = {
                    "priority": t.priority.value,
                    "estimated_effort": t.estimated_effort,
                    "labels": t.labels,
                    "subtasks": t.subtasks
                }
                self.created_at = t.created_at
                self.updated_at = t.updated_at
                self.progress = None
        
        return SimpleTaskContext(task) 