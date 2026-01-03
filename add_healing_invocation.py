#!/usr/bin/env python3
"""Add super().heal_repository() to agents with HealerMixin but missing invocation."""

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
        if 'def heal_repository' not in content:
            return False
        
        # Find heal_repository method and add super() call at the start
        lines = content.split('\n')
        new_lines = []
        i = 0
        inserted = False
        
        while i < len(lines):
            line = lines[i]
            new_lines.append(line)
            
            # Look for heal_repository method definition
            if 'def heal_repository' in line and not inserted:
                # Add the method signature
                i += 1
                while i < len(lines):
                    new_lines.append(lines[i])
                    # Look for the first non-docstring, non-comment line after method def
                    if i < len(lines) - 1:
                        next_line = lines[i + 1].strip()
                        if next_line and not next_line.startswith('"""') and not next_line.startswith("'''") and not next_line.startswith('#'):
                            # Found the first real line of code
                            i += 1
                            # Get indentation from next line
                            next_line_full = lines[i]
                            indent = len(next_line_full) - len(next_line_full.lstrip())
                            indent_str = ' ' * indent
                            
                            # Insert super().heal_repository() call
                            new_lines.append(f'{indent_str}# CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)')
                            new_lines.append(f'{indent_str}super().heal_repository()')
                            new_lines.append('')
                            inserted = True
                            break
                    i += 1
            
            i += 1
        
        if inserted:
            file_path.write_text('\n'.join(new_lines), encoding='utf-8')
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

# Find and fix all agents
root = Path('.')
fixed_count = 0
skipped_count = 0
error_count = 0

agents_to_fix = [
    'agentic_core/L0_maintenance/scripts/BootstrapAgent.py',
    'agentic_core/L0_maintenance/scripts/GuardianOrchestratorAgent.py',
    'agentic_core/L0_maintenance/scripts/HealingOrchestratorAgent.py',
    'agentic_core/L1_cognition/thought_engine/CanonDependencySentinelAgent.py',
    'agentic_core/L1_cognition/thought_engine/CognitionCanonBaseAgent.py',
    'agentic_core/L1_cognition/thought_engine/IntelligentOrchestratorAgent.py',
    'agentic_core/L1_cognition/thought_engine/MetaLearningAgent.py',
    'agentic_core/L1_cognition/thought_engine/ReflectionAgent.py',
    'agentic_core/L2_execution/ToolRegistry/ManifestManagerAgent.py',
    'agentic_core/L2_execution/ToolRegistry/McpConnectionManagerAgent.py',
    'agentic_core/L2_execution/base_agents/L2ExecutionBaseAgent.py',
]

for agent_path in agents_to_fix:
    file_path = root / agent_path.replace('/', '\\')
    if file_path.exists():
        if fix_agent_file(file_path):
            fixed_count += 1
            print(f"✓ FIXED: {agent_path}")
        else:
            skipped_count += 1
            print(f"⊘ SKIP: {agent_path}")
    else:
        error_count += 1
        print(f"✗ NOT FOUND: {agent_path}")

print(f"\n📊 Summary: {fixed_count} fixed, {skipped_count} skipped, {error_count} not found")
