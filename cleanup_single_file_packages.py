#!/usr/bin/env python3
"""Clean up single-file packages detected by Key 34."""

import shutil
from pathlib import Path

ROOT = Path(__file__).parent

# List of single-file packages to remove (from Key 34 output)
SINGLE_FILE_PACKAGES = [
    "config/runtime/synthesis/use_tools",
    "config/pipeline/synthesis/use_tools",
    "config/logic/synthesis/use_tools",
    "config/logic/validation/check_structure",
    "config/logic/validation/convert_content",
    "config/cache/data_access/get_info",
    "schemas/runtime/synthesis/use_schema_invoke",
    "schemas/pipeline/synthesis/use_schema_invoke",
    "schemas/pipeline/synthesis/use_schema_retry",
    "schemas/logic/data_access/get_schema_utility",
    "schemas/logic/synthesis/pick_best_refinement",
    "schemas/logic/synthesis/use_schema_invoke",
    "schemas/logic/validation/check_schema_safety",
    "schemas/logic/validation/convert_schema_embedding",
    "schemas/cache/data_access/get_schema_embedding",
    "schemas/cache/data_access/get_schema_request",
    "observability/pipeline/synthesis/use_tools",
    "observability/logic/synthesis/use_tools",
    "observability/logic/validation/check_structure",
    "observability/logic/validation/convert_content",
    "scripts/runtime/synthesis/use_tools_invoke",
    "scripts/pipeline/synthesis/use_tools_invoke",
    "scripts/pipeline/synthesis/use_tools_retry",
    "scripts/logic/data_access/check_rules_safety",
    "scripts/logic/data_access/get_info_utility",
    "scripts/logic/synthesis/use_tools_invoke",
    "scripts/logic/validation/check_structure_safety",
    "scripts/logic/validation/convert_embedding",
    "scripts/cache/data_access/get_info_embedding",
]

def main():
    """Remove all single-file packages."""
    removed = []
    not_found = []
    
    for pkg_path in SINGLE_FILE_PACKAGES:
        full_path = ROOT / pkg_path
        
        if not full_path.exists():
            not_found.append(pkg_path)
            continue
        
        # Verify it's a single-file package
        children = [c for c in full_path.iterdir() if c.name != "__pycache__" and not c.name.startswith(".")]
        
        if len(children) == 1 and children[0].name == "__init__.py":
            # Check if __init__.py is empty or trivial
            init_content = children[0].read_text(encoding='utf-8', errors='ignore').strip()
            
            # Remove the entire directory
            shutil.rmtree(full_path)
            removed.append(pkg_path)
            print(f"✓ Removed: {pkg_path}")
        else:
            print(f"⚠ Skipped (not single-file): {pkg_path} ({len(children)} files)")
    
    print(f"\n{'='*80}")
    print(f"CLEANUP SUMMARY")
    print(f"{'='*80}")
    print(f"Removed: {len(removed)} single-file packages")
    print(f"Not found: {len(not_found)} packages")
    print(f"Total processed: {len(SINGLE_FILE_PACKAGES)}")
    
    if not_found:
        print(f"\nNot found packages:")
        for pkg in not_found:
            print(f"  - {pkg}")

if __name__ == "__main__":
    main()
