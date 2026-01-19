#!/usr/bin/env python3
"""
Batch fix docstring issues in agent files.
Adds missing docstrings to functions and classes.
"""
import ast
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent


def get_agents_needing_fixes() -> List[Dict]:
    """Get agents with low documented_pct."""
    data = json.load(open(PROJECT_ROOT / 'agent_discovery_full.json'))
    low_doc = [
        a for a in data 
        if a.get('documented_pct', 100) < 100 
        and 'agentic_core' in a.get('path', '')
        and 'test' not in a.get('path', '').lower()
    ]
    return sorted(low_doc, key=lambda x: x.get('documented_pct', 0))


def add_missing_docstrings(source: str) -> Tuple[str, int]:
    """Add missing docstrings to functions and classes."""
    fixes = 0
    lines = source.split('\n')
    result_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        result_lines.append(line)
        
        # Check for function or class definition
        match = re.match(r'^(\s*)(async\s+)?def\s+(\w+)\s*\([^)]*\)[^:]*:\s*$', line)
        class_match = re.match(r'^(\s*)class\s+(\w+)[^:]*:\s*$', line)
        
        if match or class_match:
            if match:
                indent = match.group(1)
                func_name = match.group(3)
                is_class = False
            else:
                indent = class_match.group(1)
                func_name = class_match.group(2)
                is_class = True
            
            body_indent = indent + '    '
            
            # Check if next non-empty line is a docstring
            j = i + 1
            has_docstring = False
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line:
                    if next_line.startswith('"""') or next_line.startswith("'''"):
                        has_docstring = True
                    break
                j += 1
            
            if not has_docstring:
                # Generate docstring based on name
                if is_class:
                    doc = f'{body_indent}"""{func_name} class."""'
                elif func_name == '__init__':
                    doc = f'{body_indent}"""Initialize the instance."""'
                elif func_name == '__post_init__':
                    doc = f'{body_indent}"""Post-initialization setup."""'
                elif func_name.startswith('_'):
                    # Private method - generate from name
                    readable = func_name.lstrip('_').replace('_', ' ').capitalize()
                    doc = f'{body_indent}"""{readable}."""'
                elif 'execute' in func_name.lower():
                    doc = f'{body_indent}"""Execute the agent logic."""'
                elif 'heal' in func_name.lower():
                    doc = f'{body_indent}"""Heal repository issues."""'
                elif 'validate' in func_name.lower():
                    doc = f'{body_indent}"""Validate the input."""'
                elif 'get_' in func_name.lower():
                    readable = func_name.replace('get_', '').replace('_', ' ')
                    doc = f'{body_indent}"""Get {readable}."""'
                elif 'set_' in func_name.lower():
                    readable = func_name.replace('set_', '').replace('_', ' ')
                    doc = f'{body_indent}"""Set {readable}."""'
                elif 'is_' in func_name.lower():
                    readable = func_name.replace('is_', '').replace('_', ' ')
                    doc = f'{body_indent}"""Check if {readable}."""'
                elif 'has_' in func_name.lower():
                    readable = func_name.replace('has_', '').replace('_', ' ')
                    doc = f'{body_indent}"""Check if has {readable}."""'
                else:
                    readable = func_name.replace('_', ' ').capitalize()
                    doc = f'{body_indent}"""{readable}."""'
                
                result_lines.append(doc)
                fixes += 1
        
        i += 1
    
    return '\n'.join(result_lines), fixes


def fix_file(file_path: Path, dry_run: bool = True) -> Dict:
    """Fix docstring issues in a single file."""
    try:
        source = file_path.read_text(encoding='utf-8')
        original = source
    except Exception as e:
        return {"error": str(e), "file": str(file_path)}
    
    # Apply fixes
    source, doc_fixes = add_missing_docstrings(source)
    
    if source != original:
        if not dry_run:
            file_path.write_text(source, encoding='utf-8')
        return {
            "file": str(file_path),
            "docstring_fixes": doc_fixes,
            "applied": not dry_run
        }
    
    return {
        "file": str(file_path),
        "docstring_fixes": 0,
        "applied": False
    }


def main(dry_run: bool = True):
    """Main entry point."""
    agents = get_agents_needing_fixes()
    
    print("=" * 70)
    print(f"BATCH DOCSTRING FIX {'(DRY RUN)' if dry_run else '(LIVE)'}")
    print("=" * 70)
    print(f"Found {len(agents)} agents with documented_pct < 100%")
    
    total_fixes = 0
    files_fixed = 0
    
    for agent in agents:
        file_path = PROJECT_ROOT / agent['path']
        if not file_path.exists():
            continue
        
        result = fix_file(file_path, dry_run)
        
        if result.get('docstring_fixes', 0) > 0:
            files_fixed += 1
            total_fixes += result['docstring_fixes']
            print(f"\n{agent['class_name']} ({agent.get('documented_pct', 0):.0f}%)")
            print(f"  File: {agent['path']}")
            print(f"  Docstring fixes: {result.get('docstring_fixes', 0)}")
    
    print("\n" + "=" * 70)
    print(f"Summary:")
    print(f"  Files with fixes: {files_fixed}")
    print(f"  Total docstrings added: {total_fixes}")
    if dry_run:
        print("\nThis was a DRY RUN. Run with --live to apply changes.")
    else:
        print("\nChanges applied!")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    dry_run = "--live" not in sys.argv
    main(dry_run)
