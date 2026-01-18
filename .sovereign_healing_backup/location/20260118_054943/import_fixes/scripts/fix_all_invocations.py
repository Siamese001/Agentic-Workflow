"""Comprehensive fix for ALL heal_repository methods across the entire codebase."""
import ast
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict

from agentic_core.L5_safety.validators.structure_blueprint_2 import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

PROJECT_ROOT = Path(__file__).parent.parent

# Directories to scan for agent files
SCAN_DIRS = [
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR, 
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR
]


def has_super_heal_call(func_node: ast.FunctionDef) -> bool:
    """Check if function calls super().heal_repository()."""
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "heal_repository":
                if isinstance(node.func.value, ast.Call):
                    if isinstance(node.func.value.func, ast.Name) and node.func.value.func.id == "super":
                        return True
    return False


def find_heal_methods_in_file(filepath: Path) -> List[Tuple[ast.FunctionDef, bool, int]]:
    """Find all heal_repository methods in a file.
    
    Returns: List of (func_node, is_class_method, line_number)
    """
    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError):
        return []
    
    results = []
    
    # Walk through all nodes
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "heal_repository":
            # Check if it's a class method (has 'self' as first arg)
            is_method = bool(node.args.args and node.args.args[0].arg == 'self')
            has_super = has_super_heal_call(node)
            results.append((node, is_method, node.lineno, has_super))
    
    return results


def add_super_call_to_method(filepath: Path, func_node: ast.FunctionDef) -> bool:
    """Add super().heal_repository() call to a method."""
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    if not func_node.body:
        return False
    
    first_stmt = func_node.body[0]
    
    # Check if first statement is a docstring
    is_docstring = (
        isinstance(first_stmt, ast.Expr) and 
        isinstance(first_stmt.value, (ast.Constant, ast.Str))
    )
    
    if is_docstring and len(func_node.body) > 1:
        # Insert after docstring
        next_stmt = func_node.body[1]
        insert_line = next_stmt.lineno - 1
        ref_line = lines[insert_line]
    else:
        # Insert before first statement
        insert_line = first_stmt.lineno - 1
        ref_line = lines[insert_line]
    
    # Calculate indentation
    indent = len(ref_line) - len(ref_line.lstrip())
    indent_str = ' ' * indent
    
    # Build args from function signature (excluding self)
    args = [arg.arg for arg in func_node.args.args if arg.arg != 'self']
    args_str = ', '.join(args)
    
    # Create super call
    super_call = f"{indent_str}super().heal_repository({args_str})"
    
    # Insert
    lines.insert(insert_line, super_call)
    new_content = '\n'.join(lines)
    
    # Verify syntax
    try:
        ast.parse(new_content)
    except SyntaxError:
        return False
    
    filepath.write_text(new_content, encoding='utf-8')
    return True


def main():
    print("=== Comprehensive heal_repository invocation fix ===\n")
    
    # Find all Python files
    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = PROJECT_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(dir_path.rglob("*.py"))
    
    print(f"Scanning {len(all_files)} Python files...\n")
    
    # Analyze all files
    files_with_heal = []
    total_methods = 0
    methods_with_super = 0
    methods_without_super = 0
    standalone_functions = 0
    
    for filepath in all_files:
        methods = find_heal_methods_in_file(filepath)
        if methods:
            files_with_heal.append((filepath, methods))
            for func, is_method, line, has_super in methods:
                total_methods += 1
                if is_method:
                    if has_super:
                        methods_with_super += 1
                    else:
                        methods_without_super += 1
                else:
                    standalone_functions += 1
    
    print(f"Found {len(files_with_heal)} files with heal_repository")
    print(f"  Total functions/methods: {total_methods}")
    print(f"  Class methods with super(): {methods_with_super}")
    print(f"  Class methods WITHOUT super(): {methods_without_super}")
    print(f"  Standalone functions: {standalone_functions}")
    
    if methods_with_super + standalone_functions > 0:
        current_pct = methods_with_super / (methods_with_super + methods_without_super) * 100 if (methods_with_super + methods_without_super) > 0 else 0
        print(f"\nCurrent class method invocation: {current_pct:.1f}%")
    
    # Fix methods without super()
    if methods_without_super > 0:
        print(f"\n=== Fixing {methods_without_super} class methods ===\n")
        fixed = 0
        
        for filepath, methods in files_with_heal:
            for func, is_method, line, has_super in methods:
                if is_method and not has_super:
                    rel_path = filepath.relative_to(PROJECT_ROOT)
                    if add_super_call_to_method(filepath, func):
                        print(f"  ✓ Fixed: {rel_path}:{line}")
                        fixed += 1
                    else:
                        print(f"  ✗ Failed: {rel_path}:{line}")
        
        print(f"\nFixed {fixed}/{methods_without_super} methods")
        
        # Recalculate
        new_pct = (methods_with_super + fixed) / (methods_with_super + methods_without_super) * 100 if (methods_with_super + methods_without_super) > 0 else 0
        print(f"New class method invocation: {new_pct:.1f}%")
    else:
        print("\n✓ All class methods already have super().heal_repository() calls!")


if __name__ == "__main__":
    main()
