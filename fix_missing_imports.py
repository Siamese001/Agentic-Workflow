#!/usr/bin/env python3
"""
Fix all missing imports across the codebase systematically.
"""

from pathlib import Path
import re

def fix_missing_imports():
    """Fix missing imports in key files."""
    fixes = []
    
    # Fix 1: mcp/client.py - Missing Protocol import
    client_file = Path("agentic_core/L2_execution/mcp/client.py")
    if client_file.exists():
        content = client_file.read_text(encoding='utf-8')
        if "from typing import Protocol" not in content and "class MCPClient(Protocol):" in content:
            # Find the import section and add Protocol
            if "from typing import" in content:
                content = content.replace(
                    "from typing import",
                    "from typing import Protocol,",
                    1
                )
            else:
                # Add new import line
                content = "from typing import Protocol\n\n" + content
            
            client_file.write_text(content, encoding='utf-8')
            fixes.append("mcp/client.py - Added Protocol import")
    
    # Fix 2: structure_blueprint.py - Already fixed Path and Any
    
    # Fix 3: HierarchyAgent.py - Already fixed os import
    
    return fixes

if __name__ == "__main__":
    print("=" * 70)
    print("Fixing Missing Imports")
    print("=" * 70)
    
    fixes = fix_missing_imports()
    
    print("\n" + "=" * 70)
    print(f"Summary: {len(fixes)} fixes applied")
    for fix in fixes:
        print(f"  ✅ {fix}")
    print("=" * 70)
    
    if fixes:
        print("\n✅ Missing imports fixed")
    else:
        print("\nℹ️  No fixes needed")
