#!/usr/bin/env python3
"""Phase 4 Part 2: Batch add super().heal_repository() to agents with healing gaps."""

import re
from pathlib import Path

# Sub-batch 2-6: 5 L2 agents to fix
agents_to_fix = [
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\GitAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\ContextCuratorAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\DependencyDiplomatAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\ExecutionCanonBaseAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\MemoryArchitectAgent.py',
]

fixed_count = 0

for agent_path in agents_to_fix:
    path = Path(agent_path)
    if not path.exists():
        print(f"⊘ SKIP: {path.name} - not found")
        continue
    
    content = path.read_text(encoding='utf-8')
    
    # Check if already has super().heal_repository()
    if 'super().heal_repository()' in content:
        print(f"⊘ SKIP: {path.name} - already has super() chain")
        continue
    
    # Check if has heal_repository method
    if 'def heal_repository(self' not in content:
        print(f"⊘ SKIP: {path.name} - no heal_repository method")
        continue
    
    # Find heal_repository method and insert super() call after docstring
    # Look for: def heal_repository(...): """...""" followed by if _call_path
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Check if this is the heal_repository method definition
        if 'def heal_repository(self' in line:
            # Add the next line (decorator or docstring start)
            i += 1
            if i < len(lines):
                new_lines.append(lines[i])
            
            # Find and skip the docstring
            if '"""' in lines[i]:
                docstring_start = i
                i += 1
                # Find closing """
                while i < len(lines) and '"""' not in lines[i]:
                    new_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    new_lines.append(lines[i])  # closing """
                    i += 1
                
                # Now insert super() call before the next statement
                # Skip empty lines and comments
                while i < len(lines) and (lines[i].strip() == '' or lines[i].strip().startswith('#')):
                    new_lines.append(lines[i])
                    i += 1
                
                # Insert super().heal_repository() call
                if i < len(lines):
                    # Get indentation from next line
                    next_line = lines[i]
                    indent = len(next_line) - len(next_line.lstrip())
                    indent_str = ' ' * indent
                    
                    new_lines.append(f'{indent_str}# CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)')
                    new_lines.append(f'{indent_str}super().heal_repository()')
                    new_lines.append('')
                
                continue
        
        i += 1
    
    new_content = '\n'.join(new_lines)
    
    if new_content != content:
        path.write_text(new_content, encoding='utf-8')
        print(f"✓ FIXED: {path.name}")
        fixed_count += 1
    else:
        print(f"✗ FAIL: {path.name} - could not insert super() call")

print(f"\n✓ Sub-batch 2-6 complete: {fixed_count}/5 agents fixed")
