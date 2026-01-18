#!/usr/bin/env python3
"""
Fix duplicate const realAgentData declarations in autonomy_dashboard.html

This script removes all but the first occurrence of realAgentData.
"""
import re
from pathlib import Path

# Import SSOT for dashboard directory - NO HARDCODING
from agentic_core.L5_safety.validators.structure_blueprint_1 import DASHBOARD_DIR, get_validated_project_root

def fix_duplicates():
    """Remove duplicate realAgentData declarations."""
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
    
    print("Reading dashboard HTML...")
    html = dashboard_path.read_text(encoding='utf-8')
    
    # Find all occurrences of realAgentData declarations
    pattern = r'// Real per-agent data \(replaces generateMockAgentData\)\s*const realAgentData = \{[^}]*\};'
    matches = list(re.finditer(pattern, html, re.DOTALL))
    
    print(f"Found {len(matches)} realAgentData declarations")
    
    if len(matches) <= 1:
        print("✅ No duplicates found")
        return
    
    # Keep only the first occurrence, remove all others
    print(f"Removing {len(matches) - 1} duplicate declarations...")
    
    # Work backwards to preserve indices
    for match in reversed(matches[1:]):
        html = html[:match.start()] + html[match.end():]
    
    # Write back
    dashboard_path.write_text(html, encoding='utf-8')
    print(f"✅ Fixed! Removed {len(matches) - 1} duplicates")
    print(f"   Kept first declaration at position {matches[0].start()}")

if __name__ == "__main__":
    fix_duplicates()
