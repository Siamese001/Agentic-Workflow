#!/usr/bin/env python3
"""
Fix the remaining 10 agents with syntax errors by adding SubatomicTestingMixin.
Handles each agent individually with proper error handling.
"""
import ast
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent

agents_to_fix = {
    'DynamicModelRouterAgent': 'agentic_core/L2_execution/ToolRegistry/DynamicModelRouterAgent.py',
    'InterfaceBoundaryAgent': 'agentic_core/L2_execution/ToolRegistry/InterfaceBoundaryAgent.py',
    'MemoryArchitectAgent': 'agentic_core/L2_execution/ToolRegistry/MemoryArchitectAgent.py',
    'ImportLockAgent': 'agentic_core/L5_safety/guardrails/ImportLockAgent.py',
    'MultiProviderRouterAgent': 'agentic_core/L5_safety/guardrails/MultiProviderRouterAgent.py',
    'TestCoverageGuardianAgent': 'agentic_core/L5_safety/guardrails/TestCoverageGuardianAgent.py',
    'AutonomyGuardianAgent': 'agentic_core/L5_safety/validators/AutonomyGuardianAgent.py',
    'HygieneGuardianAgent': 'agentic_core/L5_safety/validators/HygieneGuardianAgent.py',
    'SyntaxValidatorAgent': 'agentic_core/L5_safety/validators/SyntaxValidatorAgent.py',
    'PerformanceAnalystAgent': 'agentic_core/L6_observability/agents/PerformanceAnalystAgent.py'
}

fixed = []
errors = []

for agent_name, agent_path in agents_to_fix.items():
    file_path = project_root / agent_path
    
    if not file_path.exists():
        errors.append(f"{agent_name}: File not found")
        continue
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Check if already has SubatomicTestingMixin
        if 'SubatomicTestingMixin' in content:
            print(f"⏭️  {agent_name}: Already has SubatomicTestingMixin")
            continue
        
        # Validate current syntax
        try:
            ast.parse(content)
        except SyntaxError as e:
            errors.append(f"{agent_name}: Pre-existing syntax error at line {e.lineno}: {e.msg}")
            print(f"❌ {agent_name}: Pre-existing syntax error at line {e.lineno}")
            continue
        
        # Add import if not present
        if 'from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin' not in content:
            # Find last import line
            lines = content.split('\n')
            import_idx = -1
            for i, line in enumerate(lines):
                if line.startswith(('import ', 'from ')) and 'import' in line:
                    import_idx = i
            
            if import_idx >= 0:
                lines.insert(import_idx + 1, "from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin")
                content = '\n'.join(lines)
        
        # Find class definition and add SubatomicTestingMixin
        import re
        class_pattern = rf'class\s+{agent_name}\s*\('
        match = re.search(class_pattern, content)
        
        if not match:
            errors.append(f"{agent_name}: Could not find class definition")
            print(f"❌ {agent_name}: Class definition not found")
            continue
        
        # Find the full class definition line(s)
        start = match.start()
        # Find the colon that ends the class definition
        colon_pos = content.find(':', start)
        if colon_pos == -1:
            errors.append(f"{agent_name}: Invalid class definition")
            continue
        
        class_def = content[start:colon_pos+1]
        
        # Add SubatomicTestingMixin after 'class AgentName('
        paren_pos = class_def.find('(')
        new_class_def = class_def[:paren_pos+1] + 'SubatomicTestingMixin, ' + class_def[paren_pos+1:]
        
        new_content = content[:start] + new_class_def + content[colon_pos+1:]
        
        # Validate new syntax
        try:
            ast.parse(new_content)
        except SyntaxError as e:
            errors.append(f"{agent_name}: Would introduce syntax error at line {e.lineno}: {e.msg}")
            print(f"❌ {agent_name}: Would introduce syntax error")
            continue
        
        # Write changes
        file_path.write_text(new_content, encoding='utf-8')
        fixed.append(agent_name)
        print(f"✅ {agent_name}")
        
    except Exception as e:
        errors.append(f"{agent_name}: {str(e)}")
        print(f"❌ {agent_name}: {str(e)[:80]}")

print(f"\n{'='*70}")
print("SUMMARY")
print('='*70)
print(f"Fixed: {len(fixed)}")
print(f"Errors: {len(errors)}")

if errors:
    print(f"\nErrors:")
    for e in errors:
        print(f"  {e}")

if fixed:
    print(f"\nFixed agents:")
    for a in fixed:
        print(f"  ✅ {a}")
