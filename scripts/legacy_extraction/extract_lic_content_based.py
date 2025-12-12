#!/usr/bin/env python3
"""Content-based extraction from legacy_lic archive."""

import hashlib
import shutil
from pathlib import Path
from typing import Dict, Set, List, Tuple

def get_file_hash(filepath: Path) -> str:
    """Get SHA256 hash of file content."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_existing_file_hashes() -> Dict[str, str]:
    """Get dict of filename -> content hash for existing sovereign files."""
    existing = {}
    repo_root = Path(".")
    
    sovereign_roots = {
        "agentic_core", "apps_lic", "apps_rg", "apps_shared",
        "schemas", "prompt_governance", "observability", "config",
        "data", "archives"
    }
    
    for root in sovereign_roots:
        root_path = repo_root / root
        if root_path.exists():
            for py_file in root_path.rglob("*.py"):
                if "__pycache__" in py_file.parts:
                    continue
                existing[py_file.name] = get_file_hash(py_file)
    
    return existing

def analyze_and_extract() -> None:
    """Analyze legacy files and extract unique content."""
    source_dir = Path("archives/legacy_lic")
    staging_dir = Path("archive_code")
    
    # Clean staging directory
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()
    
    existing_hashes = get_existing_file_hashes()
    
    extracted_files = []
    duplicate_files = []
    unique_content_files = []
    
    # Scan all Python files in legacy_lic
    for py_file in source_dir.rglob("*.py"):
        if "__pycache__" in py_file.parts or ".git" in py_file.parts:
            continue
            
        filename = py_file.name
        legacy_hash = get_file_hash(py_file)
        
        if filename not in existing_hashes:
            # Truly new filename
            dest_path = staging_dir / filename
            shutil.copy2(py_file, dest_path)
            extracted_files.append(filename)

        elif existing_hashes[filename] != legacy_hash:
            # Same filename but different content - might be valuable
            # Rename with _LIC suffix to preserve
            new_name = filename.replace('.py', '_LIC.py')
            dest_path = staging_dir / new_name
            shutil.copy2(py_file, dest_path)
            unique_content_files.append((filename, new_name))

        else:
            duplicate_files.append(filename)
    
    return extracted_files, unique_content_files, duplicate_files

if __name__ == "__main__":

    extracted, unique_content, duplicates = analyze_and_extract()

    if unique_content:
        #print(f"\nUnique content files ({len(unique_content)}):")
        for orig, new in sorted(unique_content):
            #print(f"  - {orig} -> {new}")
            pass
    
    if duplicates:
        #print(f"\nDuplicate files ({len(duplicates)}):")
        for f in sorted(duplicates):
            #print(f"  - {f}")
            pass
    else:
        #print("\nNo duplicate files found")
        pass
