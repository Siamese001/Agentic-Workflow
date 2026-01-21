#!/usr/bin/env python3
"""
Smart MCP hardening fix - handles edge cases like stub files, multiple classes, etc.
"""
import json
import re
import ast
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

# Load agent discovery data
data = json.load(open('agent_discovery_full.json'))
needs_hardening = [a for a in data if not a.get('mcp_hardened')]

print(f"Found {len(needs_hardening)} agents needing MCP hardening")
print()

fixed_count = 0
skipped_count = 0
errors = []

def find_agent_class_in_file(content: str, class_name: str) -> Optional[Tuple[int, int, str]]:
    """
    Find the actual agent class definition in the file.
    Returns (start_pos, end_pos, current_inheritance) or None.
    """
    # Try direct class match first
    pattern = rf'class\s+{re.escape(class_name)}\s*\((.*?)\)\s*:'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return (match.start(), match.end(), match.group(1).strip())

    # Try to find any class that ends with "Agent" and is the main one
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name == class_name:
                    # Found it via AST
                    pattern = rf'class\s+{re.escape(node.name)}\s*\((.*?)\)\s*:'
                    match = re.search(pattern, content)
                    if match:
                        return (match.start(), match.end(), match.group(1).strip())
    except:
        pass

    return None

def add_mcp_import(content: str) -> str:
    """Add MCPHardenedMixin import if not present."""
    if 'MCPHardenedMixin' in content:
        return content

    import_line = 'from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\n'

    lines = content.split('\n')
    insert_idx = 0

    # Find last import line
    for i, line in enumerate(lines):
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            insert_idx = i + 1

    # If no imports, add after module docstring
    if insert_idx == 0:
        in_docstring = False
        for i, line in enumerate(lines):
            if '"""' in line or "'''" in line:
                in_docstring = not in_docstring
                if not in_docstring:
                    insert_idx = i + 1
                    break

    lines.insert(insert_idx, import_line.rstrip())
    return '\n'.join(lines)

for agent in needs_hardening:
    path = Path(agent['path'])
    name = agent['class_name']

    if not path.exists():
        print(f"⚠️  SKIP: {name} - file not found: {path}")
        skipped_count += 1
        continue

    try:
        content = path.read_text(encoding='utf-8')

        # Check if already has MCPHardenedMixin
        if 'MCPHardenedMixin' in content:
            print(f"✓ SKIP: {name} - already has MCPHardenedMixin")
            skipped_count += 1
            continue

        # Find the class definition
        result = find_agent_class_in_file(content, name)

        if not result:
            # Try to find if this is a stub/re-export file
            if 'from agentic_core' in content and 'import' in content and name in content:
                print(f"✓ SKIP: {name} - stub/re-export file")
                skipped_count += 1
                continue

            print(f"⚠️  SKIP: {name} - class not found in file")
            skipped_count += 1
            continue

        start_pos, end_pos, current_inheritance = result

        # Build new inheritance
        if current_inheritance:
            # Check if it already has MCPHardenedMixin somehow
            if 'MCPHardenedMixin' in current_inheritance:
                print(f"✓ SKIP: {name} - already has MCPHardenedMixin in inheritance")
                skipped_count += 1
                continue
            new_inheritance = f"{current_inheritance}, MCPHardenedMixin"
        else:
            new_inheritance = "MCPHardenedMixin"

        # Replace class definition
        old_class_def = content[start_pos:end_pos]
        new_class_def = f"class {name}({new_inheritance}):"
        content = content[:start_pos] + new_class_def + content[end_pos:]

        # Add import
        content = add_mcp_import(content)

        # Write back
        path.write_text(content, encoding='utf-8')

        print(f"✅ FIXED: {name}")
        fixed_count += 1

    except Exception as e:
        error_msg = f"❌ ERROR: {name} - {str(e)}"
        print(error_msg)
        errors.append(error_msg)

print()
print("=" * 80)
print(f"SMART MCP HARDENING FIX COMPLETE")
print("=" * 80)
print(f"Fixed: {fixed_count}")
print(f"Skipped: {skipped_count}")
print(f"Errors: {len(errors)}")
print()

if errors:
    print("ERRORS:")
    for error in errors[:10]:  # Show first 10
        print(f"  {error}")
    if len(errors) > 10:
        print(f"  ... and {len(errors) - 10} more")
    print()

# Calculate new coverage
total_agents = len(data)
originally_hardened = sum(1 for a in data if a.get('mcp_hardened'))
new_hardened = originally_hardened + fixed_count
new_coverage = new_hardened / total_agents * 100

print(f"MCP Hardening Coverage:")
print(f"  Before: {originally_hardened}/{total_agents} ({originally_hardened/total_agents*100:.1f}%)")
print(f"  After:  {new_hardened}/{total_agents} ({new_coverage:.1f}%)")
print(f"  Improvement: +{fixed_count} agents (+{fixed_count/total_agents*100:.1f}%)")
print()
print(f"Next step: Update discovery and regenerate dashboard")
print(f"Command: python scripts/dashboard_e2e_pipeline_fast.py")
