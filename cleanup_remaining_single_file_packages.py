#!/usr/bin/env python3
"""Clean up remaining single-file packages exposed after first cleanup."""

import shutil
from pathlib import Path

ROOT = Path(__file__).parent

# Remaining single-file packages from second Key 34 run
REMAINING_PACKAGES = [
    "schemas/pipeline/synthesis",
    "schemas/runtime/synthesis",
    "config/cache/data_access",
    "config/runtime/synthesis",
]

def main():
    """Remove remaining single-file packages."""
    removed = []
    
    for pkg_path in REMAINING_PACKAGES:
        full_path = ROOT / pkg_path
        
        if not full_path.exists():
            print(f"⚠ Not found: {pkg_path}")
            continue
        
        # Verify it's a single-file package
        children = [c for c in full_path.iterdir() if c.name != "__pycache__" and not c.name.startswith(".")]
        
        if len(children) == 1 and children[0].name == "__init__.py":
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
    print(f"Total processed: {len(REMAINING_PACKAGES)}")

if __name__ == "__main__":
    main()
