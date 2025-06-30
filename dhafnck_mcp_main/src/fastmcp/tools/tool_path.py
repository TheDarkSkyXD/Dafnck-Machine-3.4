from pathlib import Path
import inspect
import os

def find_project_root(start_path: Path = None) -> Path:
    """
    Dynamically find the project root directory with support for multiple project locations.
    
    Priority order:
    1. PROJECT_ROOT_PATH environment variable (if set)
    2. Search upwards for ___root___ file (highest priority explicit marker)
    3. Current working directory (if it contains ___root___ file)
    4. Search upwards for .git directory
    5. Search upwards for other project markers (.cursor/rules/, etc.)
    6. Fallback to current working directory
    
    This makes the system project-agnostic and portable across different locations.

    Args:
        start_path (Path, optional): The path to start searching from. If None, uses the caller's file location.

    Returns:
        Path: The project root directory as a pathlib.Path object.
    """
    # Priority 1: Check environment variable for explicit project root
    env_project_root = os.environ.get('PROJECT_ROOT_PATH')
    if env_project_root:
        project_root = Path(env_project_root).resolve()
        if project_root.exists():
            return project_root
    
    # Priority 2: Check current working directory first for ___root___ file
    cwd = Path.cwd()
    if (cwd / "___root___").exists():
        return cwd
    
    # Priority 3: Search upwards from start_path
    if start_path is None:
        # Get the caller's file location
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        if module and hasattr(module, '__file__'):
            current = Path(module.__file__).resolve()
        else:
            current = cwd
    else:
        current = Path(start_path).resolve()
    
    # If current is a file, start from its parent
    if current.is_file():
        current = current.parent
    
    # Search upwards for ___root___ file first (highest priority)
    for parent in [current] + list(current.parents):
        if (parent / "___root___").exists():
            return parent
    
    # Search upwards for .git second (high priority)
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists():
            return parent
    
    # If no ___root___ or .git found, search for other project markers
    for parent in [current] + list(current.parents):
        if _is_project_root(parent):
            return parent
    
    # Fallback: return current working directory
    return cwd

def _is_project_root(path: Path) -> bool:
    """
    Check if a path is a project root by looking for common project markers.
    
    Args:
        path (Path): Path to check
        
    Returns:
        bool: True if path appears to be a project root
    """
    # Check for ___root___ file (highest priority explicit marker)
    if (path / "___root___").exists():
        return True
    
    # Check for .git directory (high priority)
    if (path / ".git").exists():
        return True
    
    # Check for .cursor/rules/ directory (our task management structure)
    if (path / ".cursor" / "rules").exists():
        return True
    
    # Check for other common project markers
    project_markers = [
        "pyproject.toml",
        "package.json",
        "Cargo.toml",
        "go.mod",
        "requirements.txt",
        "cursor_agent"
    ]
    
    for marker in project_markers:
        if (path / marker).exists():
            return True
    
    return False

def get_project_cursor_rules_dir(project_root: Path = None) -> Path:
    """
    Get the .cursor/rules directory for a project.
    
    Args:
        project_root (Path, optional): Project root path. If None, finds it automatically.
        
    Returns:
        Path: Path to .cursor/rules directory
    """
    if project_root is None:
        project_root = find_project_root()
    
    return project_root / ".cursor" / "rules"

def ensure_project_structure(project_root: Path = None) -> Path:
    """
    Ensure the project has the required .cursor/rules structure.
    
    Args:
        project_root (Path, optional): Project root path. If None, finds it automatically.
        
    Returns:
        Path: Path to .cursor/rules directory
    """
    if project_root is None:
        project_root = find_project_root()
    
    cursor_rules_dir = project_root / ".cursor" / "rules"
    
    # Create required directories
    directories = [
        cursor_rules_dir,
        cursor_rules_dir / "tasks",
        cursor_rules_dir / "brain",
        cursor_rules_dir / "agents"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Create required files if they don't exist
    tasks_json = cursor_rules_dir / "tasks" / "tasks.json"
    if not tasks_json.exists():
        tasks_json.write_text('{"tasks": [], "metadata": {"version": "1.0.0"}}')
    
    projects_json = cursor_rules_dir / "brain" / "projects.json"
    if not projects_json.exists():
        projects_json.write_text('{}')
    
    auto_rule_mdc = cursor_rules_dir / "auto_rule.mdc"
    if not auto_rule_mdc.exists():
        auto_rule_mdc.write_text('# Auto-generated rules\n\nThis file is automatically generated by the task management system.\n')
    
    return cursor_rules_dir 