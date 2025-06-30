"""
Pattern detection functionality for project analysis.
Handles detection of existing code patterns and frameworks.
"""

from pathlib import Path
from typing import List
from fastmcp.tools.tool_path import find_project_root


class PatternDetector:
    """Handles detection of existing code patterns and frameworks"""
    
    def __init__(self, project_root: Path = None, context_dir: Path = None):
        self.project_root = project_root or find_project_root()
        self.context_dir = context_dir or (self.project_root / ".cursor/rules/contexts")
    
    def detect_existing_patterns(self) -> List[str]:
        """Detect existing code patterns and frameworks"""
        patterns = []
        
        # Define cursor_agent directory for consistent analysis
        agent_library_dir = self.project_root / "cursor_agent"
        
        # Check for Python project indicators (only in cursor_agent directory)
        has_python_files = any(agent_library_dir.glob("**/*.py")) if agent_library_dir.exists() else False
        has_requirements_txt = (agent_library_dir / "requirements.txt").exists() or (self.project_root / "requirements.txt").exists()
        has_setup_py = (agent_library_dir / "setup.py").exists()
        has_pyproject_toml = (agent_library_dir / "pyproject.toml").exists()
        
        # Check for Node.js project indicators (only check root for package.json)
        has_package_json = (self.project_root / "package.json").exists()
        has_node_modules = (self.project_root / "node_modules").exists()
        has_js_files = any(agent_library_dir.glob("**/*.js")) or any(agent_library_dir.glob("**/*.ts")) if agent_library_dir.exists() else False
        
        # Determine primary project type based on evidence
        python_score = sum([has_python_files, has_requirements_txt, has_setup_py, has_pyproject_toml])
        nodejs_score = sum([has_package_json, has_node_modules, has_js_files])
        
        # Add primary project type first
        if python_score >= nodejs_score and python_score > 0:
            if has_requirements_txt:
                patterns.append("Python project with pip dependencies")
            else:
                patterns.append("Python project")
            
            # Only add JavaScript tooling if there are actual JS/TS files in cursor_agent directory
            # Don't add it just because package.json exists at root level
            if has_package_json and not has_node_modules and has_js_files:
                patterns.append("JavaScript tooling for validation/config")
        elif nodejs_score > 0:
            patterns.append("Node.js/JavaScript project")
            if has_python_files:
                patterns.append("Python components")
        
        # Check for other project types (only in cursor_agent directory)
        if (agent_library_dir / "Cargo.toml").exists():
            patterns.append("Rust project")
        if (agent_library_dir / "go.mod").exists():
            patterns.append("Go project")
        if (agent_library_dir / "pom.xml").exists():
            patterns.append("Java Maven project")
        
        # Add architecture patterns for Python projects (only in cursor_agent directory)
        if python_score > 0 and agent_library_dir.exists():
            if (agent_library_dir / "src").exists():
                patterns.append("Modular Python architecture")
            if any(agent_library_dir.glob("**/*cli*.py")):
                patterns.append("CLI-based application")
            if any(agent_library_dir.glob("**/models.py")):
                patterns.append("Dataclass-based models")
        
        return patterns 