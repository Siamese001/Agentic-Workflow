#!/usr/bin/env python3
"""Analyze the remaining 36 agents that need MCP hardening."""
import json
from pathlib import Path
from archives.location_violations.file_utils import safe_read_file, safe_write_file

data = json.load(open('agent_discovery_full.json'))
remaining = [a for a in data if not a.get('mcp_hardened')]

print(f"Analyzing {len(remaining)} agents still missing MCP hardening")
print("=" * 80)
print()

# Categorize by issue type
stub_files = []
no_class_found = []
fixable = []

for agent in remaining:
    path = Path(agent['path'])
    name = agent['class_name']
    
    if not path.exists():
        no_class_found.append((name, "File not found"))
        continue
    
    try:
        content = path.read_text(encoding='utf-8')
        
        # Check if stub/re-export
        if 'from agentic_core' in content and 'import' in content:
            if content.count(f"class {name}") == 0:
                stub_files.append((name, path))
                continue
        
        # Check if class exists
        if f"class {name}" not in content:
            no_class_found.append((name, "Class definition not in file"))
            continue
        
        # Check if already has MCPHardenedMixin (metadata stale)
        if 'MCPHardenedMixin' in content:
            print(f"⚠️  {name}: Already has MCPHardenedMixin (metadata stale)")
            continue
        
        # Appears fixable
        fixable.append((name, path))
    
    except Exception as e:
        no_class_found.append((name, f"Error: {e}"))

print(f"\n📊 CATEGORIZATION:")
print(f"  Stub/re-export files: {len(stub_files)}")
print(f"  Class not found: {len(no_class_found)}")
print(f"  Fixable: {len(fixable)}")
print()

if stub_files:
    print("\n🔗 STUB FILES (need to find real implementation):")
    for name, path in stub_files[:10]:
        print(f"  - {name}")
        print(f"    {path}")

if no_class_found:
    print(f"\n❌ CLASS NOT FOUND ({len(no_class_found)} agents):")
    for name, reason in no_class_found[:10]:
        print(f"  - {name}: {reason}")

if fixable:
    print(f"\n✅ FIXABLE ({len(fixable)} agents):")
    for name, path in fixable:
        print(f"  - {name}")
        print(f"    {path}")
