"""
Script to update unified_structure_subatomic.yaml with ALL .py files
to resolve Phase 1B validation by making YAML match actual filesystem
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def find_all_py_files(agentic_core_path: Path) -> list[Path]:
    """Find all .py files in agentic_core directory"""
    py_files = []
    for py_file in agentic_core_path.rglob("*.py"):
        if py_file.is_file():
            # Get relative path from agentic_core root
            rel_path = py_file.relative_to(agentic_core_path)
            py_files.append(rel_path)
    return sorted(py_files)


def add_py_to_yaml_node(yaml_data: Dict[str, Any], py_path: Path) -> bool:
    """Add .py file to the appropriate node in YAML structure"""
    current = yaml_data.get("agentic-directory", {}).get("agentic_core", {})
    
    # Navigate through the path components
    parts = py_path.parts[:-1]  # All parts except the filename
    
    for part in parts:
        if part not in current:
            # Create directory if it doesn't exist
            current[part] = {}
        current = current[part]
    
    # Add .py file to the directory
    filename = py_path.parts[-1]
    if filename not in current:
        current[filename] = None
        return True
    return False  # Already exists


def update_yaml_with_all_py_files():
    """Main function to update YAML with all .py files"""
    repo_root = Path.cwd()
    yaml_path = repo_root / "unified_structure_subatomic.yaml"
    agentic_core_path = repo_root / "agentic_core"
    
    print("Scanning for all .py files...")
    py_files = find_all_py_files(agentic_core_path)
    print(f"Found {len(py_files)} .py files")
    
    # Load current YAML
    with open(yaml_path, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
    
    # Add all .py files to YAML
    added_count = 0
    for py_file in py_files:
        if add_py_to_yaml_node(yaml_data, py_file):
            added_count += 1
            print(f"Added: {py_file}")
        else:
            print(f"Skipped (already exists): {py_file}")
    
    # Save updated YAML
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\nUpdated YAML: added {added_count} .py files")
    print(f"Total .py files found: {len(py_files)}")
    
    # Show breakdown by type
    init_files = [f for f in py_files if f.name == "__init__.py"]
    other_files = [f for f in py_files if f.name != "__init__.py"]
    print(f"__init__.py files: {len(init_files)}")
    print(f"Other .py files: {len(other_files)}")
    
    return added_count, len(py_files)


if __name__ == "__main__":
    update_yaml_with_all_py_files()
