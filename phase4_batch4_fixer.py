#!/usr/bin/env python3
"""Phase 4 Part 2 Batch 4: Aggressive final push to 65% invocation."""

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

# Scan ALL Python files in entire project
root = Path(r'C:\Git\Agentic-Workflow')
fixed_count = 0
total_checked = 0
fixed_files = []

for py_file in root.rglob('*.py'):
    # Skip test files, scripts, and generated files
    if any(skip in str(py_file) for skip in ['test', 'venv', '__pycache__', '.git', 'node_modules']):
        continue
    
    total_checked += 1
    if fix_agent_file(py_file):
        fixed_count += 1
        fixed_files.append(py_file.relative_to(root))

print(f"✓ Batch 4 complete: {fixed_count} agents fixed from {total_checked} files checked")
print(f"✓ Total fixed so far: {56 + fixed_count} agents")

if fixed_count > 0:
    print(f"\n✓ Fixed files:")
    for f in sorted(fixed_files)[:20]:
        print(f"  - {f}")
    if len(fixed_files) > 20:
        print(f"  ... and {len(fixed_files) - 20} more")
