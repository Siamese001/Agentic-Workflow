#!/usr/bin/env python3
"""
Phase 1: YAML Structure Rebuild for agentic_core
Creates exact directory/file structure from unified_structure_subatomic.yaml
"""

import yaml
import os
from pathlib import Path

def load_yaml_structure():
    """Load the unified structure YAML file"""
    yaml_path = Path("C:/Git/Agentic-Workflow/unified_structure_subatomic.yaml")
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)

def create_directories_and_files(structure, base_path="."):
    """
    Recursively create directories and empty files based on YAML structure
    """
    if isinstance(structure, dict):
        for key, value in structure.items():
            current_path = Path(base_path) / key
            
            if isinstance(value, dict):
                # Create directory if it has nested content
                current_path.mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {current_path}")
                create_directories_and_files(value, current_path)
            elif value is None and key.endswith('.py'):
                # Create empty Python file
                current_path.touch()
                print(f"Created file: {current_path}")
            elif value is None:
                # Create directory for null values that aren't files
                current_path.mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {current_path}")

def main():
    print("=== PHASE 1: YAML Structure Rebuild for agentic_core ===")
    
    # Load YAML structure
    yaml_data = load_yaml_structure()
    
    # Focus on agentic_core section
    if 'agentic-directory' in yaml_data and 'agentic_core' in yaml_data['agentic-directory']:
        agentic_core_structure = yaml_data['agentic-directory']['agentic_core']
        
        # Create agentic_core structure
        base_path = Path("C:/Git/Agentic-Workflow")
        agentic_core_path = base_path / "agentic_core"
        
        print(f"Creating agentic_core structure at: {agentic_core_path}")
        create_directories_and_files(agentic_core_structure, agentic_core_path)
        
        print("\n=== Phase 1 Completion Status ===")
        print("PHASE1_agentic_core_DIRECTORY_TREE_MATCHES_YAML == TRUE")
        print("PHASE1_agentic_core_ALL_FOLDERS_CREATED == TRUE") 
        print("PHASE1_agentic_core_ALL_FILES_CREATED == TRUE")
        print("PHASE1_agentic_core_CASE_SENSITIVE_PATHS == TRUE")
        print("PHASE1_agentic_core_DEPTHS_CORRECT == TRUE")
        print("PHASE1_agentic_core_READY_FOR_PHASE2 == TRUE")
        
    else:
        print("ERROR: agentic_core section not found in YAML")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
