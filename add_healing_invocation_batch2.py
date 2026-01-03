#!/usr/bin/env python3
"""Batch add super().heal_repository() to remaining 45 agents with HealerMixin."""

import re
from pathlib import Path
import ast

def has_heal_method(content: str) -> bool:
    """Check if file has heal_repository method."""
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == 'heal_repository':
                return True
    except:
        pass
    return False

def fix_agent_file(file_path: Path) -> bool:
    """Fix a single agent file by adding super().heal_repository() chain."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Check if already has super().heal_repository()
        if 'super().heal_repository()' in content:
            return False
        
        # Check if has heal_repository method
        if not has_heal_method(content):
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
                # Collect method signature (may span multiple lines)
                i += 1
                while i < len(lines) and not lines[i].strip().endswith(':'):
                    new_lines.append(lines[i])
                    i += 1
                
                if i < len(lines):
                    new_lines.append(lines[i])  # Add the line with ':'
                    i += 1
                
                # Skip docstring if present
                if i < len(lines):
                    stripped = lines[i].strip()
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        quote = '"""' if stripped.startswith('"""') else "'''"
                        new_lines.append(lines[i])
                        i += 1
                        
                        # Find end of docstring
                        while i < len(lines):
                            new_lines.append(lines[i])
                            if quote in lines[i] and not lines[i].strip().startswith(quote):
                                i += 1
                                break
                            i += 1
                
                # Now add super().heal_repository() at the start of actual code
                if i < len(lines):
                    next_line = lines[i]
                    indent = len(next_line) - len(next_line.lstrip())
                    indent_str = ' ' * indent
                    
                    new_lines.append(f'{indent_str}# CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)')
                    new_lines.append(f'{indent_str}super().heal_repository()')
                    new_lines.append('')
                    inserted = True
            
            i += 1
        
        if inserted:
            file_path.write_text('\n'.join(new_lines), encoding='utf-8')
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

# Find all agents with HealerMixin but no super().heal_repository()
root = Path('.')
agents_to_fix = []

for py_file in root.rglob('*.py'):
    if 'archives' in str(py_file) or 'tests' in str(py_file) or '__pycache__' in str(py_file):
        continue
    
    try:
        content = py_file.read_text(encoding='utf-8')
        
        # Check if has HealerMixin
        if 'HealerMixin' not in content:
            continue
        
        # Check if already has super().heal_repository()
        if 'super().heal_repository()' in content:
            continue
        
        # Check if has heal_repository method
        if has_heal_method(content):
            agents_to_fix.append(py_file)
    except:
        pass

# Fix all agents
fixed_count = 0
skipped_count = 0

for file_path in sorted(agents_to_fix):
    if fix_agent_file(file_path):
        fixed_count += 1
        rel_path = file_path.relative_to(root)
        print(f"✓ FIXED: {rel_path}")
    else:
        skipped_count += 1

print(f"\n📊 Summary: {fixed_count} fixed, {skipped_count} skipped")
