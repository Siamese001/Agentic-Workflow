#!/usr/bin/env python3
"""
Bulk fix heal invocation for all agents missing super().heal_repository() calls.

This script:
1. Identifies agents with healing capability but no invocation
2. Adds super().heal_repository() calls to their heal_repository methods
3. Handles various method signature patterns
"""
import json
import re
from pathlib import Path
from typing import List, Tuple

# Load agent discovery data
data = json.load(open('agent_discovery_full.json'))

# Find agents needing invocation
needs_invocation = [
    a for a in data 
    if a.get('has_healing') and a.get('invocation') != 'Yes'
]

print(f"Found {len(needs_invocation)} agents needing heal invocation fix")
print()

fixed_count = 0
skipped_count = 0
errors = []

for agent in needs_invocation:
    path = Path(agent['path'])
    name = agent['class_name']
    
    if not path.exists():
        print(f"⚠️  SKIP: {name} - file not found: {path}")
        skipped_count += 1
        continue
    
    try:
        content = path.read_text(encoding='utf-8')
        
        # Find heal_repository method
        # Pattern: def heal_repository(...): with various signatures
        pattern = r'(    def heal_repository\([^)]*\)[^:]*:.*?)(\n        (?:""".*?"""|\'\'\'.*?\'\'\')\s*\n)?(.*?)(\n    def |\n\nclass |\Z)'
        
        matches = list(re.finditer(pattern, content, re.DOTALL))
        
        if not matches:
            print(f"⚠️  SKIP: {name} - no heal_repository method found")
            skipped_count += 1
            continue
        
        match = matches[0]
        method_sig = match.group(1)
        docstring = match.group(2) or ""
        method_body = match.group(3)
        next_section = match.group(4)
        
        # Check if super() call already exists
        if 'super().heal_repository' in method_body or 'super().__init__' in method_body:
            print(f"✓ SKIP: {name} - already has super() call")
            skipped_count += 1
            continue
        
        # Find the first non-comment, non-docstring line
        lines = method_body.split('\n')
        insert_index = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                insert_index = i
                break
        
        # Insert super() call before the first real line
        indent = "        "  # 8 spaces for method body
        super_call = f"{indent}super().heal_repository()\n"
        
        lines.insert(insert_index, super_call)
        new_method_body = '\n'.join(lines)
        
        # Reconstruct the method
        new_method = method_sig + docstring + new_method_body + next_section
        
        # Replace in content
        new_content = content[:match.start()] + new_method + content[match.end():]
        
        # Write back
        path.write_text(new_content, encoding='utf-8')
        
        print(f"✅ FIXED: {name}")
        fixed_count += 1
        
    except Exception as e:
        error_msg = f"❌ ERROR: {name} - {str(e)}"
        print(error_msg)
        errors.append(error_msg)

print()
print("=" * 80)
print(f"HEAL INVOCATION FIX COMPLETE")
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

print(f"Next step: Run agent discovery to update invocation status")
print(f"Command: python scripts/agent_discovery.py")
