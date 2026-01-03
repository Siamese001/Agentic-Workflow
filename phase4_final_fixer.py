#!/usr/bin/env python3
"""Phase 4 Final Push: Fix ALL remaining agents with healing gaps to reach 65% invocation."""

import re
from pathlib import Path

def fix_agent_file(file_path: Path) -> bool:
    """Fix a single agent file by adding super().heal_repository() chain."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Check if already has super().heal_repository()
        if 'super().heal_repository()' in content:
            return False
        
        # Check if has heal_repository method
        if 'def heal_repository(self' not in content:
            return False
        
        # Find heal_repository method and insert super() call after docstring
        lines = content.split('\n')
        new_lines = []
        i = 0
        inserted = False
        
        while i < len(lines):
            line = lines[i]
            new_lines.append(line)
            
            # Check if this is the heal_repository method definition
            if 'def heal_repository(self' in line and not inserted:
                # Add the next line (decorator or docstring start)
                i += 1
                if i < len(lines):
                    new_lines.append(lines[i])
                
                # Find and skip the docstring
                if i < len(lines) and '"""' in lines[i]:
                    i += 1
                    # Find closing """
                    while i < len(lines) and '"""' not in lines[i]:
                        new_lines.append(lines[i])
                        i += 1
                    if i < len(lines):
                        new_lines.append(lines[i])  # closing """
                        i += 1
                    
                    # Now insert super() call before the next statement
                    # Skip empty lines
                    while i < len(lines) and lines[i].strip() == '':
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
                        inserted = True
                    
                    continue
            
            i += 1
        
        new_content = '\n'.join(new_lines)
        
        if new_content != content:
            file_path.write_text(new_content, encoding='utf-8')
            return True
        
        return False
    except Exception as e:
        return False

# Target the remaining flagged agents from the report
remaining_agents = [
    r'C:\Git\Agentic-Workflow\agentic_core\L0_maintenance\scripts\BootstrapAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L0_maintenance\scripts\MaintenanceBaseAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\NervousSystemAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\OrchestrationBaseAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\P1CoreSemanticTerritoryMapperAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\P1CoreTerritoryHealerAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\SubatomicHopAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L4_state\ValidationContext\PineconeSovereignAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L4_state\ValidationContext\RedisSovereignAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L4_state\ValidationContext\StateBaseAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L4_state\ValidationContext\SubAtomicRegistryAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L5_safety\gravity\ImportAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L5_safety\guardrails\BiasDetectorAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L5_safety\guardrails\ConstitutionalReviewerAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L5_safety\guardrails\CostGovernorAgent.py',
]

# Also scan for any remaining agents with gaps
root = Path(r'C:\Git\Agentic-Workflow')
fixed_count = 0
fixed_files = []

# First fix the explicitly flagged agents
for agent_path in remaining_agents:
    path = Path(agent_path)
    if path.exists() and fix_agent_file(path):
        fixed_count += 1
        fixed_files.append(path.relative_to(root))

# Then scan entire project for any remaining gaps
for py_file in root.rglob('*.py'):
    if any(skip in str(py_file) for skip in ['test', 'venv', '__pycache__', '.git', 'node_modules']):
        continue
    
    if fix_agent_file(py_file):
        fixed_count += 1
        fixed_files.append(py_file.relative_to(root))

print(f"✓ Final push complete: {fixed_count} agents fixed")
print(f"✓ Total fixed in Phase 4: {71 + fixed_count} agents")

if fixed_files:
    print(f"\n✓ Fixed files:")
    for f in sorted(set(fixed_files))[:30]:
        print(f"  - {f}")
    if len(set(fixed_files)) > 30:
        print(f"  ... and {len(set(fixed_files)) - 30} more")
