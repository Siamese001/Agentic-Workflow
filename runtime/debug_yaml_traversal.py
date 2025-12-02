"""
Debug script to trace YAML traversal step by step
"""

import yaml
from pathlib import Path

def debug_yaml_extraction():
    repo_root = Path.cwd()
    yaml_path = repo_root / "unified_structure_subatomic.yaml"
    
    # Load YAML
    with open(yaml_path, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
    
    print("YAML top-level keys:", list(yaml_data.keys()))
    
    # Navigate to agentic_core
    agentic_dir = yaml_data.get("agentic-directory", {})
    print("agentic-directory keys:", list(agentic_dir.keys()))
    
    agentic_core = agentic_dir.get("agentic_core", {})
    print("agentic_core type:", type(agentic_core))
    print("agentic_core keys (first 10):", list(agentic_core.keys())[:10])
    
    # Manual traversal to find .py files
    files = []
    directories = []
    
    def traverse_tree(node: dict, current_path: str = "agentic_core", depth=0):
        if depth > 10:  # Prevent infinite recursion
            return
        
        if isinstance(node, dict):
            for key, value in node.items():
                full_path = f"{current_path}/{key}"
                
                if key.endswith('.py'):
                    print(f"Found file: {full_path}")
                    files.append(full_path)
                else:
                    print(f"Found dir: {full_path}")
                    directories.append(full_path)
                    if isinstance(value, dict):
                        traverse_tree(value, full_path, depth + 1)
    
    print("\nStarting traversal...")
    traverse_tree(agentic_core)
    
    print(f"\nResults:")
    print(f"Directories found: {len(directories)}")
    print(f"Files found: {len(files)}")
    
    if files:
        print("First 5 files:")
        for i, file_path in enumerate(sorted(files)[:5]):
            print(f"  {i+1}: {file_path}")

if __name__ == "__main__":
    debug_yaml_extraction()
