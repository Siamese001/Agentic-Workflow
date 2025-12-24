#!/usr/bin/env python3
"""
Fix circular imports in agentic_core by converting absolute imports to relative imports.

This script:
1. Scans all Python files in agentic_core/
3. Converts them to relative imports: from .L1_cognition... or from ..L1_cognition...
4. Preserves imports from outside agentic_core (e.g., from apps_shared, from schemas)
"""

import re
from pathlib import Path
from typing import Any, Optional, Protocol, Dict, List
from typing import List, Tuple

def calculate_relative_import(file_path: Path, import_path: str, project_root: Path) -> str:
    """
    Calculate the correct relative import path.
    
    Args:
        file_path: Path to the file being modified
        import_path: The import path after 'agentic_core.' (e.g., 'L1_cognition.planning.types')
        project_root: Root of the agentic_core package
        
    Returns:
        Relative import path (e.g., '.planning.types' or '..L1_cognition.planning.types')
    """
    # Get the directory containing the file
    file_dir = file_path.parent
    
    # Get relative path from agentic_core root to file directory
    try:
        rel_to_core = file_dir.relative_to(project_root)
    except ValueError:
        # File is at agentic_core root
        rel_to_core = Path(".")
    
    # Split the import path
    import_parts = import_path.split(".")
    
    # Split the file's relative path
    if str(rel_to_core) == ".":
        file_parts = []
    else:
        file_parts = list(rel_to_core.parts)
    
    # Calculate how many levels up we need to go
    # If importing from same directory, use '.'
    # If importing from sibling, use '.sibling'
    # If importing from parent's sibling, use '..sibling'
    
    if len(file_parts) == 0:
        # File is at agentic_core root, importing from subdirectory
        return f".{import_path}"
    
    # Check if first part of import matches first part of file path
    if len(import_parts) > 0 and len(file_parts) > 0 and import_parts[0] == file_parts[0]:
        # Same L1 directory
        if len(file_parts) == 1:
            # File is directly in L1 directory
            if len(import_parts) == 1:
                return "."
            else:
                return f".{'.'.join(import_parts[1:])}"
        else:
            # File is deeper in L1 directory
            # Need to go up to common ancestor
            common_depth = 1
            for i in range(1, min(len(file_parts), len(import_parts))):
                if file_parts[i] == import_parts[i]:
                    common_depth = i + 1
                else:
                    break
            
            levels_up = len(file_parts) - common_depth
            remaining_import = ".".join(import_parts[common_depth:])
            
            if levels_up == 0:
                return f".{remaining_import}" if remaining_import else "."
            else:
                dots = "." * (levels_up + 1)
                return f"{dots}{remaining_import}" if remaining_import else dots
    else:
        # Different L1 directory - go up to agentic_core root
        levels_up = len(file_parts)
        dots = "." * (levels_up + 1)
        return f"{dots}{import_path}"
    
    # Default: go up one level
    return f"..{import_path}"


def fix_imports_in_file(file_path: Path, agentic_core_root: Path, dry_run: bool = False) -> Tuple[int, List[str]]:
    """
    Fix imports in a single file.
    
    Returns:
        Tuple of (number of changes, list of changes made)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return 0, [f"ERROR reading {file_path}: {e}"]
    
    original_content = content
    changes = []
    
    # Pattern to match: from agentic_core.SOMETHING import ...
    pattern = r'^(\s*)from agentic_core\.([a-zA-Z0-9_\.]+) import (.+)$'
    
    lines = content.split('\n')
    modified_lines = []
    
    for line in lines:
        match = re.match(pattern, line)
        if match:
            indent = match.group(1)
            import_path = match.group(2)
            imported_items = match.group(3)
            
            # Calculate relative import
            relative_path = calculate_relative_import(file_path, import_path, agentic_core_root)
            
            # Create new import line
            new_line = f"{indent}from {relative_path} import {imported_items}"
            modified_lines.append(new_line)
            
            changes.append(f"  {line.strip()} -> {new_line.strip()}")
        else:
            modified_lines.append(line)
    
    new_content = '\n'.join(modified_lines)
    
    if new_content != original_content and not dry_run:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception as e:
            return 0, [f"ERROR writing {file_path}: {e}"]
    
    num_changes = len(changes)
    return num_changes, changes


def main():
    """Main execution function."""
    # Get agentic_core root
    script_dir = Path(__file__).parent
    agentic_core_root = script_dir / "agentic_core"
    
    if not agentic_core_root.exists():
        print(f"ERROR: agentic_core directory not found at {agentic_core_root}")
        return
    
    print("=" * 80)
    print("FIXING CIRCULAR IMPORTS IN AGENTIC_CORE")
    print("=" * 80)
    print(f"Root: {agentic_core_root}")
    print()
    
    # Find all Python files
    py_files = list(agentic_core_root.rglob("*.py"))
    print(f"Found {len(py_files)} Python files")
    print()
    
    # Process each file
    total_changes = 0
    files_modified = 0
    
    for py_file in py_files:
        num_changes, changes = fix_imports_in_file(py_file, agentic_core_root, dry_run=False)
        
        if num_changes > 0:
            files_modified += 1
            total_changes += num_changes
            rel_path = py_file.relative_to(agentic_core_root)
            print(f"✓ {rel_path} ({num_changes} changes)")
            for change in changes:
                print(change)
            print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files scanned: {len(py_files)}")
    print(f"Files modified: {files_modified}")
    print(f"Total changes: {total_changes}")
    print()
    print("✓ Circular import fix complete!")


if __name__ == "__main__":
    main()