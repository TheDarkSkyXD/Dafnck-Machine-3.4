#!/usr/bin/env python3
"""
YAML JSON Formatting Fix Script

This script fixes JSON formatting issues in YAML files across the agent library.
It converts single-line JSON format strings to properly formatted multi-line YAML.

Issues Fixed:
1. Single-line JSON strings with escaped quotes
2. Long JSON examples that are hard to read
3. Inconsistent formatting across agent specification files

Usage:
    python fix_yaml_json_formatting.py [--dry-run] [--path PATH]
"""

import os
import re
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YAMLJSONFormatter:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.files_processed = 0
        self.files_modified = 0
        self.errors = []
        
    def find_yaml_files(self, root_path: str) -> List[Path]:
        """Find all YAML files in the agent library."""
        yaml_files = []
        for root, dirs, files in os.walk(root_path):
            # Skip backup directories
            if any(backup in root for backup in ['.yaml-lib-backup', 'yaml-lib-backup']):
                continue
                
            for file in files:
                if file.endswith(('.yaml', '.yml')):
                    yaml_files.append(Path(root) / file)
        return yaml_files
    
    def extract_json_from_format_string(self, format_str: str) -> Tuple[str, str, str]:
        """Extract JSON part from format string and return (prefix, json_part, suffix)."""
        # Pattern to match JSON objects/arrays in format strings
        json_patterns = [
            r'(.*?Example:\s*)(\{.*\})(.*)',
            r'(.*?Example:\s*)(\[.*\])(.*)',
            r'(.*?schema:\s*)(\{.*\})(.*)',
            r'(.*?)(\{.*\})(.*)',
            r'(.*?)(\[.*\])(.*)'
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, format_str, re.DOTALL)
            if match:
                prefix = match.group(1).strip()
                json_part = match.group(2)
                suffix = match.group(3).strip() if len(match.groups()) > 2 else ""
                
                # Try to parse as JSON to validate, or check for placeholder patterns
                try:
                    # Clean up the JSON string
                    cleaned_json = self.clean_json_string(json_part)
                    json.loads(cleaned_json)
                    return prefix, cleaned_json, suffix
                except json.JSONDecodeError:
                    # Check if it's a placeholder JSON pattern (contains {...} or [...])
                    if ('{' in json_part and '}' in json_part) or ('[' in json_part and ']' in json_part):
                        # Format placeholder JSON for better readability
                        formatted_placeholder = self.format_placeholder_json(json_part)
                        return prefix, formatted_placeholder, suffix
                    continue
        
        return "", "", ""
    
    def clean_json_string(self, json_str: str) -> str:
        """Clean and format JSON string."""
        # Remove extra whitespace
        json_str = json_str.strip()
        
        # Fix common issues
        json_str = json_str.replace("''", '"')  # Fix double single quotes
        json_str = re.sub(r'(?<!\\)"', '"', json_str)  # Ensure proper quotes
        
        # Try to parse and reformat
        try:
            parsed = json.loads(json_str)
            return json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            # If parsing fails, return cleaned version
            return json_str
    
    def format_placeholder_json(self, json_str: str) -> str:
        """Format placeholder JSON with {...} and [...] for better readability."""
        # Remove extra whitespace
        json_str = json_str.strip()
        
        # Fix common quote issues
        json_str = json_str.replace("''", '"')
        
        # Try to make it more readable by adding line breaks
        # Look for patterns like {"key": {...}, "key2": [...]}
        formatted = json_str
        
        # Add line breaks after commas in objects
        formatted = re.sub(r',\s*"', ',\n  "', formatted)
        
        # Add line breaks after opening braces
        formatted = re.sub(r'{\s*"', '{\n  "', formatted)
        
        # Add line breaks before closing braces
        formatted = re.sub(r'"\s*}', '"\n}', formatted)
        
        # Clean up multiple consecutive newlines
        formatted = re.sub(r'\n\s*\n', '\n', formatted)
        
        return formatted
    
    def format_yaml_content(self, content: str) -> Tuple[str, bool]:
        """Format YAML content by fixing JSON format strings."""
        lines = content.split('\n')
        modified = False
        result_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this line contains a format field with JSON
            if re.match(r'\s*format:\s*[\'"].*[\'"]', line):
                # Extract the format value
                format_match = re.match(r'(\s*format:\s*[\'"])(.*?)([\'"])\s*$', line)
                if format_match:
                    indent = format_match.group(1)
                    format_value = format_match.group(2)
                    quote_char = format_match.group(3)
                    
                    # Check if it contains JSON
                    prefix, json_part, suffix = self.extract_json_from_format_string(format_value)
                    
                    if json_part:
                        # Convert to multi-line format
                        base_indent = len(indent) - len(indent.lstrip())
                        yaml_indent = ' ' * base_indent
                        content_indent = ' ' * (base_indent + 2)
                        
                        # Build the new multi-line format
                        new_lines = [f"{yaml_indent}format: |"]
                        
                        # Add the prefix if it exists
                        if prefix:
                            new_lines.append(f"{content_indent}{prefix}")
                            if json_part:
                                new_lines.append(f"{content_indent}")  # Empty line separator
                        
                        # Add formatted JSON
                        json_lines = json_part.split('\n')
                        for json_line in json_lines:
                            if json_line.strip():
                                new_lines.append(f"{content_indent}{json_line}")
                        
                        # Add suffix if it exists
                        if suffix:
                            new_lines.append(f"{content_indent}")  # Empty line separator
                            new_lines.append(f"{content_indent}{suffix}")
                        
                        result_lines.extend(new_lines)
                        modified = True
                        logger.debug(f"Converted format field: {format_value[:50]}...")
                    else:
                        result_lines.append(line)
                else:
                    result_lines.append(line)
            else:
                result_lines.append(line)
            
            i += 1
        
        return '\n'.join(result_lines), modified
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single YAML file."""
        try:
            self.files_processed += 1
            
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Format the content
            formatted_content, modified = self.format_yaml_content(original_content)
            
            if modified:
                if not self.dry_run:
                    # Write the formatted content back
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(formatted_content)
                
                self.files_modified += 1
                logger.info(f"{'[DRY RUN] ' if self.dry_run else ''}Fixed: {file_path}")
                return True
            
            return False
            
        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            self.errors.append(error_msg)
            logger.error(error_msg)
            return False
    
    def process_directory(self, directory_path: str) -> Dict[str, Any]:
        """Process all YAML files in a directory."""
        logger.info(f"Processing directory: {directory_path}")
        
        # Find all YAML files
        yaml_files = self.find_yaml_files(directory_path)
        logger.info(f"Found {len(yaml_files)} YAML files")
        
        # Process each file
        for file_path in yaml_files:
            self.process_file(file_path)
        
        # Return summary
        return {
            'files_found': len(yaml_files),
            'files_processed': self.files_processed,
            'files_modified': self.files_modified,
            'errors': self.errors
        }

def main():
    parser = argparse.ArgumentParser(description='Fix JSON formatting in YAML files')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    parser.add_argument('--path', type=str, 
                       default='dhafnck_mcp_main/agent-library',
                       help='Path to process (default: dhafnck_mcp_main/agent-library)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize formatter
    formatter = YAMLJSONFormatter(dry_run=args.dry_run)
    
    # Process the directory
    if not os.path.exists(args.path):
        logger.error(f"Path does not exist: {args.path}")
        return 1
    
    logger.info(f"Starting YAML JSON formatting fix {'(DRY RUN)' if args.dry_run else ''}")
    
    results = formatter.process_directory(args.path)
    
    # Print summary
    print("\n" + "="*60)
    print("YAML JSON FORMATTING FIX SUMMARY")
    print("="*60)
    print(f"Files found: {results['files_found']}")
    print(f"Files processed: {results['files_processed']}")
    print(f"Files modified: {results['files_modified']}")
    print(f"Errors: {len(results['errors'])}")
    
    if results['errors']:
        print("\nErrors encountered:")
        for error in results['errors']:
            print(f"  - {error}")
    
    if args.dry_run:
        print(f"\nThis was a dry run. Run without --dry-run to apply changes.")
    else:
        print(f"\nAll changes have been applied successfully!")
    
    return 0 if not results['errors'] else 1

if __name__ == '__main__':
    exit(main()) 