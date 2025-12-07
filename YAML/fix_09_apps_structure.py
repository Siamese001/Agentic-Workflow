import logging
from __future__ import annotations
#!/usr/bin/env python3
"""
Fix nested folder structure in 09_apps domain.
This script flattens the self-referential nesting in apps_lic and apps_rg
by moving content from the deepest level to the proper depth.
"""

import shutil
from pathlib import Path
import sys

def flatten_nested_structure(base_path: Path, nested_dir: str) -> None:
    """
    Flatten nested structure like apps_lic/apps_lic/apps_lic/.../apps_lic/
    to proper apps_lic/ structure.
    """
    logging.debug(f"Fixing nested structure in {nested_dir}...")
    
    nested_path = base_path / nested_dir
    if not nested_path.exists():
        logging.debug(f"  {nested_dir} does not exist, skipping")
        return
    
    # Find the deepest level that contains actual content
    current = nested_path
    while True:
        next_level = current / nested_dir
        if next_level.exists() and any(next_level.iterdir()):
            current = next_level
            logging.debug(f"  Found deeper level: {current.relative_to(base_path)}")
        else:
            break
    
    logging.debug(f"  Deepest content level: {current.relative_to(base_path)}")
    
    # Create backup of original structure
    backup_path = base_path / f"{nested_dir}_backup"
    if nested_path.exists() and not backup_path.exists():
        logging.debug(f"  Creating backup: {backup_path}")
        shutil.copytree(nested_path, backup_path)
    
    # Move content BEFORE removing the original structure
    logging.debug(f"  Moving content to proper structure...")
    
    # Move all content from deepest level to proper location
    for item in current.iterdir():
        if item.name == nested_dir:  # Skip the final empty nested dir
            continue
            
        target = nested_path / item.name
        logging.debug(f"    Moving {item.relative_to(base_path)} -> {target.relative_to(base_path)}")
        
        if target.exists():
            if item.is_file():
                target.unlink()
            else:
                shutil.rmtree(target)
        
        shutil.move(str(item), str(target))
    
    # Create __init__.py if missing
    init_file = nested_path / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        logging.debug(f"  Created {init_file.relative_to(base_path)}")
    
    logging.debug(f"  Fixed {nested_dir} structure")

def main():
    """Main function to fix 09_apps structure."""
    base_path = Path("C:/Git/Agentic-Workflow/09_apps")
    
    if not base_path.exists():
        logging.debug(f"Error: {base_path} does not exist")
        sys.exit(1)
    
    logging.debug("Fixing 09_apps nested folder structure...")
    
    # Fix both apps_lic and apps_rg
    for nested_dir in ["apps_lic", "apps_rg"]:
        flatten_nested_structure(base_path, nested_dir)
    
    logging.debug("Structure fix complete!")

if __name__ == "__main__":
    main()
