#!/usr/bin/env python3
"""
Debug script to check file collection logic.
"""

from pathlib import Path
from typing import Dict

def get_actual_apps_structure(apps_path: str):
    """Get the actual apps/ directory structure."""
    root = Path(apps_path)
    structure: Dict[str, Dict] = {}
    
    if not root.exists():
        return structure
    
    for layer_dir in root.iterdir():
        if not layer_dir.is_dir():
            continue
            
        layer_name = layer_dir.name
        structure[layer_name] = {}
        
        for phase_dir in layer_dir.iterdir():
            if not phase_dir.is_dir():
                continue
                
            phase_name = phase_dir.name
            structure[layer_name][phase_name] = {}
            
            # Walk the full hierarchy for non-shared layers
            if layer_name != 'shared':
                for ops_dir in phase_dir.iterdir():
                    if not ops_dir.is_dir():
                        continue
                        
                    ops_name = ops_dir.name
                    structure[layer_name][phase_name][ops_name] = {}
                    
                    for general_dir in ops_dir.iterdir():
                        if not general_dir.is_dir():
                            continue
                            
                        general_name = general_dir.name
                        structure[layer_name][phase_name][ops_name][general_name] = {}
                        
                        for utility_dir in general_dir.iterdir():
                            if not utility_dir.is_dir():
                                continue
                                
                            utility_name = utility_dir.name
                            structure[layer_name][phase_name][ops_name][general_name][utility_name] = {}
                            
                            for helper_dir in utility_dir.iterdir():
                                if not helper_dir.is_dir():
                                    continue
                                    
                                helper_name = helper_dir.name
                                structure[layer_name][phase_name][ops_name][general_name][utility_name][helper_name] = []
                                
                                # List files
                                for file_path in helper_dir.iterdir():
                                    if file_path.is_file():
                                        structure[layer_name][phase_name][ops_name][general_name][utility_name][helper_name].append(file_path.name)
    
    return structure

def collect_all_files_debug(structure, path=""):
    """Debug version of file collection."""
    files = []
    
    print(f"Debug: Processing path '{path}', type: {type(structure)}")
    
    if isinstance(structure, dict):
        print(f"Debug: Dict with keys: {list(structure.keys())}")
        for key, value in structure.items():
            new_path = f"{path}/{key}" if path else key
            files.extend(collect_all_files_debug(value, new_path))
    elif isinstance(structure, list):
        print(f"Debug: List with {len(structure)} items at path '{path}'")
        for item in structure:
            files.append(f"{path}/{item}")
            print(f"Debug: Found file: {path}/{item}")
    else:
        print(f"Debug: Unexpected type {type(structure)} at path '{path}'")
    
    return files

def main():
    """Debug main function."""
    apps_path = "apps"
    
    print("🔍 DEBUGGING FILE COLLECTION")
    print("=" * 40)
    
    # Get structure
    print("📁 Getting structure...")
    actual_structure = get_actual_apps_structure(apps_path)
    
    # Show a sample of the structure
    print("\n📋 Structure sample:")
    layer_name = list(actual_structure.keys())[0] if actual_structure else "None"
    print(f"   First layer: {layer_name}")
    
    if layer_name in actual_structure:
        phase_name = list(actual_structure[layer_name].keys())[0] if actual_structure[layer_name] else "None"
        print(f"   First phase: {phase_name}")
        
        if phase_name in actual_structure[layer_name]:
            # Drill down to show file structure
            current = actual_structure[layer_name][phase_name]
            path_parts = [layer_name, phase_name]
            
            while isinstance(current, dict) and current:
                next_key = list(current.keys())[0]
                path_parts.append(next_key)
                current = current[next_key]
                print(f"   {' -> '.join(path_parts)}: {type(current)} with {len(current) if isinstance(current, (dict, list)) else 'N/A'} items")
                
                if isinstance(current, list):
                    print(f"   Files found: {current[:3]}...")  # Show first 3 files
                    break
    
    # Collect all files
    print("\n📂 Collecting all files...")
    all_files = collect_all_files_debug(actual_structure)
    
    print("\n📊 RESULTS:")
    print(f"   Total files collected: {len(all_files)}")
    if all_files:
        print(f"   Sample files:")
        for f in all_files[:5]:
            print(f"      - {f}")
    else:
        print("   No files collected!")

if __name__ == "__main__":
    main()
