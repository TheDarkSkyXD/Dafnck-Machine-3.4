#!/usr/bin/env python3
"""
Update deprecated environment variables script
Updates all AGENT_LIBRARY_DIR* and AGENT_LIBRARY_DIR_PATH references to use only AGENT_LIBRARY_DIR_PATH
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

def get_project_root() -> Path:
    """Get the project root directory"""
    current_dir = Path(__file__).parent
    if current_dir.name == "dhafnck_mcp_main":
        return current_dir
    return current_dir / "dhafnck_mcp_main"

def find_files_to_update(root_dir: Path) -> List[Path]:
    """Find all files that might contain deprecated environment variables"""
    patterns = [
        "**/*.py",
        "**/*.sh",
        "**/*.json",
        "**/*.md",
        "**/*.tsx",
        "**/*.ts",
        "**/*.yml",
        "**/*.yaml",
        "**/Dockerfile*",
        "**/.env*",
        "**/env.*"
    ]
    
    files = []
    for pattern in patterns:
        files.extend(root_dir.glob(pattern))
    
    # Also check parent directory for frontend files
    parent_dir = root_dir.parent
    if parent_dir.exists():
        for pattern in patterns:
            files.extend(parent_dir.glob(pattern))
    
    # Filter out common directories to skip
    skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
    filtered_files = []
    
    for file_path in files:
        if file_path.is_file() and not any(skip_dir in file_path.parts for skip_dir in skip_dirs):
            filtered_files.append(file_path)
    
    return filtered_files

def get_replacement_patterns() -> List[Tuple[str, str, str]]:
    """Get all replacement patterns (regex, replacement, description)"""
    return [
        # Environment variable names
        (r'\bCURSOR_AGENT_DIR_PATH\b', 'AGENT_LIBRARY_DIR_PATH', 'Environment variable name'),
        (r'\bAGENT_YAML_LIB_PATH\b', 'AGENT_LIBRARY_DIR_PATH', 'Environment variable name'),
        
        # Path references in environment variables
        (r'"dhafnck_mcp_main/agent-library"', '"dhafnck_mcp_main/agent-library"', 'Path in env var'),
        (r"'dhafnck_mcp_main/agent-library'", "'dhafnck_mcp_main/agent-library'", 'Path in env var'),
        (r'dhafnck_mcp_main/agent-library', 'dhafnck_mcp_main/agent-library', 'Path reference'),
        (r'/app/agent-library', '/app/agent-library', 'Docker path'),
        
        # Variable names in code
        (r'\bagent_library_dir\b(?=\s*[=:])', 'agent_library_dir', 'Variable name assignment'),
        (r'"agent_library_dir":', '"agent_library_dir":', 'JSON key'),
        (r"'agent_library_dir':", "'agent_library_dir':", 'JSON key'),
        
        # Method names
        (r'get_agent_library_dir\b', 'get_agent_library_dir', 'Method name'),
        
        # Comments and documentation
        (r'agent_library_dir', 'agent_library_dir', 'Variable in comments'),
        (r'AGENT_LIBRARY_DIR(?!_PATH)', 'AGENT_LIBRARY_DIR', 'Constant name'),
    ]

def update_file_content(file_path: Path, patterns: List[Tuple[str, str, str]]) -> Tuple[bool, List[str]]:
    """Update a single file with the replacement patterns"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        for pattern, replacement, description in patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                changes_made.append(f"  - {description}: {len(matches)} replacements")
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes_made
        
        return False, []
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, []

def update_call_agent_py_specifically(root_dir: Path) -> bool:
    """Specifically update call_agent.py with correct logic"""
    call_agent_path = root_dir / "src/fastmcp/task_management/application/use_cases/call_agent.py"
    
    if not call_agent_path.exists():
        print(f"call_agent.py not found at {call_agent_path}")
        return False
    
    try:
        with open(call_agent_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the environment variable logic at the bottom
        old_pattern = r'''# Global initialization for backwards compatibility
if "AGENT_LIBRARY_DIR_PATH" in os\.environ:
    AGENT_LIBRARY_DIR = resolve_path\(os\.environ\["AGENT_LIBRARY_DIR_PATH"\]\)
elif "AGENT_LIBRARY_DIR_PATH" in os\.environ:
    AGENT_LIBRARY_DIR = resolve_path\(os\.environ\["AGENT_LIBRARY_DIR_PATH"\]\)
else:
    # Default fallback paths
    project_root = resolve_path\(os\.getcwd\(\)\)
    AGENT_LIBRARY_DIR = project_root / "yaml-lib"
    if not AGENT_LIBRARY_DIR\.exists\(\):
        AGENT_LIBRARY_DIR = project_root / "dhafnck_mcp_main/agent-library"'''
        
        new_pattern = '''# Global initialization for backwards compatibility
if "AGENT_LIBRARY_DIR_PATH" in os.environ:
    AGENT_LIBRARY_DIR = resolve_path(os.environ["AGENT_LIBRARY_DIR_PATH"])
else:
    # Default fallback paths
    project_root = resolve_path(os.getcwd())
    AGENT_LIBRARY_DIR = project_root / "agent-library"
    if not AGENT_LIBRARY_DIR.exists():
        AGENT_LIBRARY_DIR = project_root / "dhafnck_mcp_main/agent-library"'''
        
        content = re.sub(old_pattern, new_pattern, content, flags=re.MULTILINE | re.DOTALL)
        
        # Replace the variable name throughout the file
        content = re.sub(r'\bAGENT_LIBRARY_DIR\b', 'AGENT_LIBRARY_DIR', content)
        
        with open(call_agent_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated call_agent.py with correct environment variable logic")
        return True
        
    except Exception as e:
        print(f"❌ Error updating call_agent.py: {e}")
        return False

def main():
    """Main function to update all deprecated environment variables"""
    print("🔄 Starting update of deprecated environment variables...")
    
    root_dir = get_project_root()
    print(f"📁 Project root: {root_dir}")
    
    # Get all files to update
    files_to_update = find_files_to_update(root_dir)
    print(f"📄 Found {len(files_to_update)} files to check")
    
    # Get replacement patterns
    patterns = get_replacement_patterns()
    
    # Update files
    updated_files = []
    total_changes = 0
    
    for file_path in files_to_update:
        try:
            relative_path = file_path.relative_to(root_dir.parent)
        except ValueError:
            relative_path = file_path
            
        was_updated, changes = update_file_content(file_path, patterns)
        
        if was_updated:
            updated_files.append(str(relative_path))
            total_changes += len(changes)
            print(f"✅ Updated: {relative_path}")
            for change in changes:
                print(change)
        
    # Specifically update call_agent.py
    update_call_agent_py_specifically(root_dir)
    
    print(f"\n🎉 Update completed!")
    print(f"📊 Files updated: {len(updated_files)}")
    print(f"🔧 Total changes: {total_changes}")
    
    if updated_files:
        print(f"\n📋 Updated files:")
        for file_path in sorted(updated_files):
            print(f"  - {file_path}")
    
    print(f"\n✅ All deprecated environment variables have been updated to use AGENT_LIBRARY_DIR_PATH")
    print(f"✅ All paths have been updated to use agent-library structure")

if __name__ == "__main__":
    main() 