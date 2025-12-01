#!/usr/bin/env python3
"""
AGENTIC_CORE ARCHIVE INVENTORY
Phase 1: Preservation catalog for Phase 2 Tier 1 restoration
Catalogs all existing .py files in agentic_core for Phase 2 Tier 1 preservation
"""

import os
import hashlib
from pathlib import Path

# Archive inventory structure
AGENTIC_CORE_ARCHIVE = {
    "metadata": {
        "purpose": "Phase 2 Tier 1 source code preservation",
        "reconstruction_date": "2025-12-01",
        "original_structure": "budget-manager-layer, executor-microagent-layer, l5_safety, observer-microagent-layer, planner-microagent-layer, retriever-microagent-layer, router-microagent-layer, safety-guard-layer",
        "target_structure": "plan-layer, orc-layer, exec-layer, mem-layer, safe-layer"
    },
    "files": {}
}

def catalog_file(filepath, relative_path):
    """Catalog a single file with content and metadata"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Calculate file hash for integrity
        file_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Determine semantic mapping based on filename and path
        semantic_mapping = map_to_target_structure(relative_path)
        
        return {
            "original_path": relative_path,
            "content": content,
            "hash": file_hash,
            "size_bytes": len(content.encode()),
            "semantic_mapping": semantic_mapping
        }
    except Exception as e:
        return {
            "original_path": relative_path,
            "error": str(e),
            "content": None
        }

def map_to_target_structure(relative_path):
    """Map old structure to new YAML structure based on semantic analysis"""
    path_lower = relative_path.lower()
    
    # Layer mappings
    if 'planner' in path_lower:
        return "plan-layer"
    elif 'executor' in path_lower:
        return "exec-layer"
    elif 'router' in path_lower or 'orchestrat' in path_lower:
        return "orc-layer"
    elif 'retriever' in path_lower or 'memory' in path_lower:
        return "mem-layer"
    elif 'safety' in path_lower or 'guard' in path_lower:
        return "safe-layer"
    elif 'observer' in path_lower or 'budget' in path_lower:
        return "safe-layer"  # Budget and observation map to safety/cost management
    else:
        return "shared"  # Default to shared if uncertain

def build_agentic_core_inventory():
    """Build complete inventory of agentic_core"""
    base_path = Path("c:/Users/amita/Documents/Work/AI Job Search/AI/ML/DL/GenAI/LLM 101/LLM Pipelines/Resume Gen/Git/Agentic-Workflow/agentic_core")
    
    if not base_path.exists():
        print(f"ERROR: agentic_core directory not found at {base_path}")
        return
    
    print("Building agentic_core archive inventory...")
    
    # Walk through all Python files
    for py_file in base_path.rglob("*.py"):
        relative_path = py_file.relative_to(base_path)
        file_info = catalog_file(py_file, str(relative_path))
        AGENTIC_CORE_ARCHIVE["files"][str(relative_path)] = file_info
        print(f"Cataloged: {relative_path} -> {file_info.get('semantic_mapping', 'unknown')}")
    
    # Save inventory
    import json
    inventory_path = base_path.parent / "agentic_core_phase1_inventory.json"
    with open(inventory_path, 'w', encoding='utf-8') as f:
        json.dump(AGENTIC_CORE_ARCHIVE, f, indent=2, ensure_ascii=False)
    
    print(f"Inventory saved to: {inventory_path}")
    print(f"Total files cataloged: {len(AGENTIC_CORE_ARCHIVE['files'])}")

if __name__ == "__main__":
    build_agentic_core_inventory()
