#!/usr/bin/env python3
"""
Update import paths for lifecycle_trace_contract after relocation.
"""

import pathlib
import sys

def update_imports():
    """Update import statements to use new path."""
    root = pathlib.Path(".")
    count = 0
    
    for py_file in root.rglob("*.py"):
        # Skip archive directories
        if "archive" in py_file.parts or ".git" in py_file.parts:
            continue
        
        try:
            content = py_file.read_text(encoding="utf-8")
            original = content
            
            # Update import paths
            content = content.replace(
                "from agentic_core.runtime.contracts.lifecycle_trace_contract import",
                "from agentic_core.runtime.contracts.lifecycle_trace_contract import"
            )
            
            if content != original:
                py_file.write_text(content, encoding="utf-8")
                count += 1
                print(f"Updated: {py_file}")
        except Exception as e:
            print(f"Error processing {py_file}: {e}", file=sys.stderr)
    
    print(f"\nTotal files updated: {count}")

if __name__ == "__main__":
    update_imports()
