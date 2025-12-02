#!/usr/bin/env python3
"""
Script to fix dataclass field ordering issues for mypy compliance
"""

import ast
from pathlib import Path
from typing import List

def fix_dataclass_field_ordering(file_path: Path) -> bool:
    """Fix dataclass field ordering in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Find dataclass definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a dataclass
                has_dataclass_decorator = any(
                    (isinstance(decorator, ast.Name) and decorator.id == 'dataclass') or
                    (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and decorator.func.id == 'dataclass')
                    for decorator in node.decorator_list
                )
                
                if has_dataclass_decorator:
                    # Find annotated assignments (dataclass fields)
                    fields = []
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign):
                            has_default = item.value is not None
                            fields.append((item, has_default))
                    
                    # Check if fields with defaults come before fields without defaults
                    seen_default = False
                    needs_fix = False
                    for field, has_default in fields:
                        if has_default:
                            seen_default = True
                        elif seen_default:
                            needs_fix = True
                            break
                    
                    if needs_fix:
                        print(f"Dataclass field ordering issue found in {file_path}")
                        return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    schemas_dir = Path("schemas")
    python_files = list(schemas_dir.rglob("*.py"))
    python_files = [f for f in python_files if f.name != "__init__.py"]
    
    files_with_issues = []
    
    for file_path in python_files:
        if fix_dataclass_field_ordering(file_path):
            files_with_issues.append(file_path)
    
    print(f"\nFound {len(files_with_issues)} files with dataclass field ordering issues:")
    for f in files_with_issues:
        print(f"  {f}")

if __name__ == "__main__":
    main()
