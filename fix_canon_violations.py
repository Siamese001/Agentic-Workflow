#!/usr/bin/env python3
"""Auto-fix canon validator violations."""

import os
import ast
import re
from pathlib import Path
from typing import List, Set, Tuple

def find_functions_with_many_params(max_params: int = 8) -> List[Tuple[str, int, int]]:
    """Find functions with too many parameters."""
    violations = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                params = len(node.args.args)
                                if params > max_params:
                                    violations.append((str(filepath), node.lineno, params))
                except:
                    continue
    return violations

def find_large_functions(max_lines: int = 50) -> List[Tuple[str, int, int]]:
    """Find functions that are too large."""
    violations = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        tree = ast.parse(''.join(lines))
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                # Count lines in function
                                start = node.lineno - 1
                                end = node.end_lineno if hasattr(node, 'end_lineno') else start + 1
                                func_lines = end - start
                                if func_lines > max_lines:
                                    violations.append((str(filepath), node.lineno, func_lines))
                except:
                    continue
    return violations

def find_duplicate_imports() -> List[str]:
    """Find files with duplicate imports."""
    violations = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        tree = ast.parse(content)
                        imports = []
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.Import, ast.ImportFrom)):
                                imports.append(ast.dump(node))
                        if len(imports) != len(set(imports)):
                            violations.append(str(filepath))
                except:
                    continue
    return violations

def find_missing_docstrings() -> List[Tuple[str, int, str]]:
    """Find functions/classes missing docstrings."""
    violations = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                                # Skip if has docstring
                                if (node.body and 
                                    isinstance(node.body[0], ast.Expr) and 
                                    isinstance(node.body[0].value, ast.Constant) and 
                                    isinstance(node.body[0].value.value, str)):
                                    continue
                                violations.append((str(filepath), node.lineno, node.name))
                except:
                    continue
    return violations

def fix_unused_variables(filepath: str) -> int:
    """Remove unused variables from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple heuristic: remove assignments that are never used
        lines = content.split('\n')
        fixed_lines = []
        removed = 0
        
        for line in lines:
            # Skip obvious unused variable assignments
            if (re.match(r'^\s*\w+\s*=\s*.+$', line) and 
                'import' not in line and 
                'def' not in line and 
                'class' not in line and
                not line.strip().endswith('_')):
                # Check if variable is used later
                var_name = line.split('=')[0].strip()
                if var_name not in content[line.find(line) + len(line):]:
                    removed += 1
                    continue
            fixed_lines.append(line)
        
        if removed > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fixed_lines))
        
        return removed
    except:
        return 0

def main():
    """Run auto-fixes for canon violations."""
    print("=== Canon Violation Auto-Fixer ===\n")
    
    # Check current violations
    print("1. Checking functions with too many parameters...")
    param_violations = find_functions_with_many_params()
    print(f"   Found {len(param_violations)} violations")
    for filepath, line, count in param_violations[:5]:
        print(f"   - {filepath}:{line} ({count} params)")
    
    print("\n2. Checking large functions...")
    large_violations = find_large_functions()
    print(f"   Found {len(large_violations)} violations")
    for filepath, line, count in large_violations[:5]:
        print(f"   - {filepath}:{line} ({count} lines)")
    
    print("\n3. Checking duplicate imports...")
    import_violations = find_duplicate_imports()
    print(f"   Found {len(import_violations)} violations")
    for filepath in import_violations[:5]:
        print(f"   - {filepath}")
    
    print("\n4. Checking missing docstrings...")
    docstring_violations = find_missing_docstrings()
    print(f"   Found {len(docstring_violations)} violations")
    for filepath, line, name in docstring_violations[:5]:
        print(f"   - {filepath}:{line} ({name})")
    
    # Auto-fix unused variables
    print("\n5. Auto-fixing unused variables...")
    total_removed = 0
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                removed = fix_unused_variables(str(filepath))
                total_removed += removed
    
    print(f"   Removed {total_removed} unused variables")
    
    print("\n=== Summary ===")
    print("To achieve 100% canon compliance, you need to:")
    print("1. Fix functions with too many parameters (split into smaller functions)")
    print("2. Break down large functions (>50 lines)")
    print("3. Remove duplicate imports")
    print("4. Add docstrings to all functions/classes")
    print("5. Fix remaining unused variables (auto-fixed some)")

if __name__ == "__main__":
    main()
