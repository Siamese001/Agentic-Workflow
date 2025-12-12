#!/usr/bin/env python3
"""Clean up final single-file packages exposed after cascading cleanup."""

import shutil
from pathlib import Path

ROOT = Path(__file__).parent

# Final single-file packages from third Key 34 run
FINAL_PACKAGES = [
    "config/cache",
    "config/runtime",
]

def main():
    """Remove final single-file packages."""
    removed = []
    
    for pkg_path in FINAL_PACKAGES:
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
    print(f"Total processed: {len(FINAL_PACKAGES)}")

if __name__ == "__main__":
    main()
