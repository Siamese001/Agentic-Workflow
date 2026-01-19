#!/usr/bin/env python3
"""
Bulk fix MCP hardening for all agents missing MCPHardenedMixin.

This script:
1. Identifies agents without MCP hardening
2. Adds MCPHardenedMixin to their class inheritance
3. Adds necessary import statements
"""
import json
import re
from pathlib import Path
from typing import List, Dict
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

# Load agent discovery data
data = json.load(open('agent_discovery_full.json'))

# Find agents needing MCP hardening
needs_hardening = [
    a for a in data 
    if not a.get('mcp_hardened')
]

print(f"Found {len(needs_hardening)} agents needing MCP hardening")
print()

fixed_count = 0
skipped_count = 0
errors = []

for agent in needs_hardening:
    path = Path(agent['path'])
    name = agent['class_name']
    
    if not path.exists():
        print(f"⚠️  SKIP: {name} - file not found: {path}")
        skipped_count += 1
        continue
    
    try:
        content = path.read_text(encoding='utf-8')
        
        # Check if MCPHardenedMixin is already imported or in inheritance
        if 'MCPHardenedMixin' in content:
            print(f"✓ SKIP: {name} - already has MCPHardenedMixin")
            skipped_count += 1
            continue
        
        # Find class definition
        class_pattern = rf'class {re.escape(name)}\s*\((.*?)\)\s*:'
        match = re.search(class_pattern, content, re.DOTALL)
        
        if not match:
            print(f"⚠️  SKIP: {name} - class definition not found")
            skipped_count += 1
            continue
        
        current_inheritance = match.group(1).strip()
        
        # Determine new inheritance
        if current_inheritance:
            # Add MCPHardenedMixin to existing inheritance
            new_inheritance = f"{current_inheritance}, MCPHardenedMixin"
        else:
            # Only MCPHardenedMixin
            new_inheritance = "MCPHardenedMixin"
        
        # Replace class definition
        new_class_def = f"class {name}({new_inheritance}):"
        old_class_def = match.group(0)
        content = content.replace(old_class_def, new_class_def)
        
        # Add import if needed
        if 'from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin' not in content:
            # Find where to insert import
            import_section_end = 0
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    import_section_end = i + 1
            
            # Insert import after last import
            if import_section_end > 0:
                lines.insert(import_section_end, 'from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin')
            else:
                # No imports found, add at top after docstring
                insert_idx = 0
                in_docstring = False
                for i, line in enumerate(lines):
                    if '"""' in line or "'''" in line:
                        in_docstring = not in_docstring
                        if not in_docstring:
                            insert_idx = i + 1
                            break
                lines.insert(insert_idx, 'from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin')
            
            content = '\n'.join(lines)
        
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
print(f"MCP HARDENING FIX COMPLETE")
print("=" * 80)
print(f"Fixed: {fixed_count}")
print(f"Skipped: {skipped_count}")
print(f"Errors: {len(errors)}")
print()

if errors:
    print("ERRORS:")
    for error in errors:
        print(f"  {error}")
    print()

print(f"Next step: Update discovery metadata and regenerate dashboard")
print(f"Command: python scripts/dashboard_e2e_pipeline_fast.py")
