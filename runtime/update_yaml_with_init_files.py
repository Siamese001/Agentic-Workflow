"""
Script to update unified_structure_subatomic.yaml with __init__.py files
to resolve Phase 1B protected path violations (Option A)
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def find_init_files(agentic_core_path: Path) -> list[Path]:
    """Find all __init__.py files in agentic_core directory"""
    init_files = []
    for init_file in agentic_core_path.rglob("__init__.py"):
        if init_file.is_file():
            # Get relative path from agentic_core root
            rel_path = init_file.relative_to(agentic_core_path)
            init_files.append(rel_path)
    return sorted(init_files)


def add_init_to_yaml_node(yaml_data: Dict[str, Any], init_path: Path) -> bool:
    """Add __init__.py to the appropriate node in YAML structure"""
    current = yaml_data.get("agentic-directory", {}).get("agentic_core", {})
    
    # Navigate through the path components
    parts = init_path.parts[:-1]  # All parts except "__init__.py"
    
    for part in parts:
        if part not in current:
            return False  # Directory doesn't exist in YAML
        current = current[part]
    
    # Add __init__.py file to the directory
    if "__init__.py" not in current:
        current["__init__.py"] = None
        return True
    return False  # Already exists


def update_yaml_with_init_files():
    """Main function to update YAML with __init__.py files"""
    repo_root = Path.cwd()
    yaml_path = repo_root / "unified_structure_subatomic.yaml"
    agentic_core_path = repo_root / "agentic_core"
    
    print("Scanning for __init__.py files...")
    init_files = find_init_files(agentic_core_path)
    print(f"Found {len(init_files)} __init__.py files")
    
    # Load current YAML
    with open(yaml_path, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
    
    # Add __init__.py files to YAML
    added_count = 0
    for init_file in init_files:
        if add_init_to_yaml_node(yaml_data, init_file):
            added_count += 1
            print(f"Added: {init_file}")
        else:
            print(f"Skipped (already exists or missing dir): {init_file}")
    
    # Save updated YAML
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\nUpdated YAML: added {added_count} __init__.py files")
    print(f"Total __init__.py files found: {len(init_files)}")
    
    return added_count, len(init_files)


if __name__ == "__main__":
    update_yaml_with_init_files()
