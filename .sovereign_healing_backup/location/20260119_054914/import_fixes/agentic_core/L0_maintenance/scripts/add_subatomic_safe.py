#!/usr/bin/env python3
"""
Safely add SubatomicTestingMixin to agents without tests.
This version handles multi-line class definitions and validates syntax.
"""
import json
import re
import ast
from pathlib import Path
import sys
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load agents without tests
with open(project_root / "agent_discovery_full.json", 'r', encoding='utf-8') as f:
    agents = json.load(f)

no_tests = [a for a in agents if not a.get('has_tests', False)]
print(f"Found {len(no_tests)} agents without tests\n")

# Process in batches by territory for easier review
territories = {}
for agent in no_tests:
    territory = agent.get('territory', 'Unknown')
    if territory not in territories:
        territories[territory] = []
    territories[territory].append(agent)

modified = []
errors = []

for territory, ags in sorted(territories.items()):
    print(f"\n{'='*70}")
    print(f"Territory: {territory} ({len(ags)} agents)")
    print('='*70)
    
    for agent in ags:
        agent_path = project_root / agent['path']
        class_name = agent['class_name']
        
        if not agent_path.exists():
            errors.append(f"{class_name}: File not found")
            continue
        
        try:
            content = agent_path.read_text(encoding='utf-8')
            
            # Check if already has SubatomicTestingMixin
            if 'SubatomicTestingMixin' in content:
                print(f"  ⏭️  {class_name}: Already has SubatomicTestingMixin")
                continue
            
            # Check if already has test_self method
            if re.search(r'def\s+test_self\s*\(', content):
                print(f"  ⏭️  {class_name}: Already has test_self method")
                continue
            
            # Validate current syntax
            try:
                ast.parse(content)
            except SyntaxError as e:
                errors.append(f"{class_name}: Pre-existing syntax error at line {e.lineno}")
                print(f"  ❌ {class_name}: Pre-existing syntax error")
                continue
            
            # Find class definition (handles multi-line)
            class_pattern = rf'class\s+{re.escape(class_name)}\s*\([^)]*\):'
            match = re.search(class_pattern, content, re.DOTALL)
            
            if not match:
                errors.append(f"{class_name}: Could not find class definition")
                print(f"  ❌ {class_name}: Class definition not found")
                continue
            
            class_def = match.group(0)
            
            # Add SubatomicTestingMixin to inheritance
            # Find the opening parenthesis
            paren_start = class_def.find('(')
            paren_end = class_def.rfind(')')
            
            if paren_start == -1 or paren_end == -1:
                errors.append(f"{class_name}: Invalid class definition")
                continue
            
            current_inheritance = class_def[paren_start+1:paren_end].strip()
            new_inheritance = f"SubatomicTestingMixin, {current_inheritance}"
            new_class_def = class_def[:paren_start+1] + new_inheritance + class_def[paren_end:]
            
            # Replace in content
            new_content = content.replace(class_def, new_class_def)
            
            # Add import if not present
            if 'from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin' not in new_content:
                # Find last import line
                import_lines = [i for i, line in enumerate(new_content.split('\n')) if line.startswith(('import ', 'from '))]
                if import_lines:
                    lines = new_content.split('\n')
                    insert_idx = import_lines[-1] + 1
                    lines.insert(insert_idx, "from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin")
                    new_content = '\n'.join(lines)
            
            # Validate new syntax
            try:
                ast.parse(new_content)
            except SyntaxError as e:
                errors.append(f"{class_name}: New syntax error at line {e.lineno}")
                print(f"  ❌ {class_name}: Would introduce syntax error")
                continue
            
            # Write changes
            agent_path.write_text(new_content, encoding='utf-8')
            modified.append(class_name)
            print(f"  ✅ {class_name}")
            
        except Exception as e:
            errors.append(f"{class_name}: {str(e)}")
            print(f"  ❌ {class_name}: {str(e)[:50]}")

print(f"\n{'='*70}")
print("SUMMARY")
print('='*70)
print(f"Modified: {len(modified)}")
print(f"Errors: {len(errors)}")

if errors:
    print(f"\nErrors ({len(errors)}):")
    for e in errors[:20]:
        print(f"  {e}")

print(f"\nNext steps:")
print(f"1. Run: python scripts/full_agent_discovery.py --force")
print(f"2. Run: python scripts/analyze_compliance.py")
print(f"3. Verify test coverage increased")
