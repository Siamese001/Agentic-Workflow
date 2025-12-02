"""
Debug script to check YAML vs filesystem path extraction
"""

import yaml
from pathlib import Path
from phase_1a_validation import YamlValidator, FilesystemScanner

def main():
    repo_root = Path.cwd()
    
    # Test YAML extraction
    yaml_validator = YamlValidator(repo_root / "unified_structure_subatomic.yaml")
    yaml_loaded, yaml_msg = yaml_validator.load_yaml()
    print(f"YAML loaded: {yaml_loaded}")
    
    if yaml_loaded:
        yaml_dirs, yaml_files = yaml_validator.extract_yaml_paths()
        print(f"YAML files found: {len(yaml_files)}")
        print("First 5 YAML files:")
        for i, file_path in enumerate(sorted(yaml_files)[:5]):
            print(f"  {i+1}: {file_path}")
        
        # Count __init__.py files in YAML
        init_files = [f for f in yaml_files if f.endswith("__init__.py")]
        print(f"__init__.py files in YAML: {len(init_files)}")
    
    # Test filesystem extraction
    fs_scanner = FilesystemScanner(repo_root)
    fs_dirs, fs_files = fs_scanner.scan_agentic_core()
    print(f"\nFS files found: {len(fs_files)}")
    print("First 5 FS files:")
    for i, file_path in enumerate(sorted(fs_files)[:5]):
        print(f"  {i+1}: {file_path}")
    
    # Count __init__.py files in FS
    init_files = [f for f in fs_files if f.endswith("__init__.py")]
    print(f"__init__.py files in FS: {len(init_files)}")
    
    # Compare first few files
    print("\nComparison (first 10 files):")
    yaml_sorted = sorted(yaml_files)
    fs_sorted = sorted(fs_files)
    
    for i in range(min(10, len(yaml_sorted), len(fs_sorted))):
        match = yaml_sorted[i] == fs_sorted[i]
        print(f"  YAML: {yaml_sorted[i]}")
        print(f"  FS:   {fs_sorted[i]}")
        print(f"  Match: {match}")
        print()

if __name__ == "__main__":
    main()
