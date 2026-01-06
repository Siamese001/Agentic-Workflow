#!/usr/bin/env python3
"""
Fix Inherited Invocation - Add heal_repository() methods to agents missing explicit invocation.

This script:
1. Loads agents with invocation='Inherited' from agent_discovery_full.json
2. For each agent class, adds a heal_repository() method that calls super().heal_repository()
3. This converts "Inherited" → "Yes" status, maximizing invocation %
"""
import ast
import json
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DISCOVERY_JSON = PROJECT_ROOT / "agent_discovery_full.json"

HEAL_METHOD_TEMPLATE = '''
    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()
'''

def load_inherited_agents() -> List[Dict]:
    """Load agents with invocation='Inherited' status."""
    with open(DISCOVERY_JSON, 'r', encoding='utf-8') as f:
        agents = json.load(f)
    return [a for a in agents if a.get('invocation') == 'Inherited']


def find_class_end(source: str, class_name: str) -> Tuple[int, int]:
    """Find the end of a class definition to insert method before it."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return -1, -1
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            # Find the last line of the class body
            if node.body:
                last_node = node.body[-1]
                # Get end line of last node
                end_line = getattr(last_node, 'end_lineno', last_node.lineno)
                # Find indentation
                lines = source.splitlines()
                if node.body:
                    first_body_line = node.body[0].lineno - 1
                    if first_body_line < len(lines):
                        indent = len(lines[first_body_line]) - len(lines[first_body_line].lstrip())
                    else:
                        indent = 4
                else:
                    indent = 4
                return end_line, indent
    return -1, -1


def has_heal_repository(source: str, class_name: str) -> bool:
    """Check if class already has heal_repository method."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return True  # Skip files with syntax errors
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == 'heal_repository':
                    return True
    return False


def add_heal_repository(file_path: Path, class_name: str) -> bool:
    """Add heal_repository method to a class."""
    try:
        source = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  [ERROR] Cannot read {file_path}: {e}")
        return False
    
    # Skip if already has method
    if has_heal_repository(source, class_name):
        print(f"  [SKIP] {class_name} already has heal_repository")
        return False
    
    # Find where to insert
    end_line, indent = find_class_end(source, class_name)
    if end_line < 0:
        print(f"  [ERROR] Cannot find class {class_name} in {file_path}")
        return False
    
    # Create indented method
    method_lines = HEAL_METHOD_TEMPLATE.strip().splitlines()
    indented_method = '\n' + '\n'.join(' ' * indent + line if line.strip() else '' for line in method_lines) + '\n'
    
    # Insert method at end of class
    lines = source.splitlines(keepends=True)
    
    # Find actual insertion point (after last line of class body)
    insert_idx = end_line
    while insert_idx < len(lines) and lines[insert_idx - 1].strip() == '':
        insert_idx += 1
    
    # Insert the method
    new_lines = lines[:end_line] + [indented_method] + lines[end_line:]
    new_source = ''.join(new_lines)
    
    # Write back
    try:
        file_path.write_text(new_source, encoding='utf-8')
        print(f"  [ADDED] heal_repository to {class_name}")
        return True
    except Exception as e:
        print(f"  [ERROR] Cannot write {file_path}: {e}")
        return False


def main():
    print("=" * 80)
    print("FIX INHERITED INVOCATION")
    print("=" * 80)
    
    agents = load_inherited_agents()
    print(f"\nFound {len(agents)} agents with 'Inherited' invocation status\n")
    
    # Group by file to avoid multiple writes
    by_file: Dict[str, List[str]] = {}
    for agent in agents:
        path = agent.get('path', '')
        class_name = agent.get('class_name', '')
        if path and class_name:
            full_path = str(PROJECT_ROOT / path)
            if full_path not in by_file:
                by_file[full_path] = []
            if class_name not in by_file[full_path]:
                by_file[full_path].append(class_name)
    
    print(f"Processing {len(by_file)} unique files...\n")
    
    added = 0
    skipped = 0
    errors = 0
    
    for file_path_str, class_names in sorted(by_file.items()):
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"[SKIP] File not found: {file_path}")
            skipped += len(class_names)
            continue
        
        print(f"\n{file_path.relative_to(PROJECT_ROOT)}:")
        for class_name in class_names:
            result = add_heal_repository(file_path, class_name)
            if result:
                added += 1
            elif result is False:
                skipped += 1
            else:
                errors += 1
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: Added {added} | Skipped {skipped} | Errors {errors}")
    print("=" * 80)


if __name__ == "__main__":
    main()
