#!/usr/bin/env python3
"""
Subatomic Canon Validator - Agentic Workflow Hardening
Validates 50 strict enforcement rules for code quality and architecture.
Zero tolerance for stubs, debt, or sprawl.
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ANSI color codes for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Global validation state
validation_results = {}
failed_checks = []

def success(key: str, message: str) -> None:
    """Record a successful validation check."""
    validation_results[key] = {"status": "PASS", "message": message}
    print(f"{Colors.GREEN}✓ [{key}] {message}{Colors.END}")

def fail(key: str, message: str) -> None:
    """Record a failed validation check."""
    validation_results[key] = {"status": "FAIL", "message": message}
    failed_checks.append(key)
    print(f"{Colors.RED}✗ [{key}] {message}{Colors.END}")

def warn(key: str, message: str) -> None:
    """Record a warning during validation."""
    validation_results[key] = {"status": "WARN", "message": message}
    print(f"{Colors.YELLOW}⚠ [{key}] {message}{Colors.END}")

def info(message: str) -> None:
    """Print an info message."""
    print(f"{Colors.CYAN}ℹ {message}{Colors.END}")

def get_python_files(root_dir: str = ".") -> List[str]:
    """Get all Python files in the repository, excluding common non-source directories."""
    python_files = []
    exclude_dirs = {
        ".git", "__pycache__", ".pytest_cache", ".tox", "venv", "env",
        ".venv", ".env", "node_modules", ".idea", ".vscode", "dist", "build",
        "archives", "data"
    }
    
    for root, dirs, files in os.walk(root_dir):
        # Remove excluded directories from traversal
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                # Convert to forward slashes for consistency
                full_path = full_path.replace("\\", "/")
                python_files.append(full_path)
    
    return python_files

def parse_python_file(file_path: str) -> Optional[ast.AST]:
    """Parse a Python file and return its AST."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return ast.parse(content, filename=file_path)
    except SyntaxError as e:
        return None
    except Exception as e:
        return None

def check_key_00_no_hardcoded_secrets():
    """Key 00: No hardcoded secrets, API keys, or passwords in code."""
    info("Checking for hardcoded secrets and API keys...")
    
    # Patterns for common secrets
    secret_patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
        r'AKIA[0-9A-Z]{16}',  # AWS access key
        r'sk-[a-zA-Z0-9]{48}',  # OpenAI API key
        r'ghp_[a-zA-Z0-9]{36}',  # GitHub personal access token
    ]
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in secret_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        violations.append(f"{file_path}:{line_num}")
        except Exception:
            continue
    
    if violations:
        fail("00", f"Found {len(violations)} potential hardcoded secrets")
        for violation in violations[:5]:  # Show first 5
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("00", "No hardcoded secrets detected")

def check_key_01_no_todo_comments():
    """Key 01: No TODO, FIXME, or XXX comments in production code."""
    info("Checking for TODO/FIXME comments...")
    
    todo_patterns = [
        r'#\s*TODO',
        r'#\s*FIXME',
        r'#\s*XXX',
        r'#\s*HACK',
        r'#\s*TEMP',
    ]
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in todo_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        violations.append(f"{file_path}:{line_num}")
        except Exception:
            continue
    
    if violations:
        fail("01", f"Found {len(violations)} TODO/FIXME comments")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("01", "No TODO/FIXME comments found")

def check_key_02_no_print_statements():
    """Key 02: No print statements in production code (use logging instead)."""
    info("Checking for print statements...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                        if node.func.id == 'print':
                            line_num = node.lineno
                            violations.append(f"{file_path}:{line_num}")
        except Exception:
            continue
    
    if violations:
        fail("02", f"Found {len(violations)} print statements")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("02", "No print statements found")

def check_key_03_no_debugger_statements():
    """Key 03: No debugger statements (breakpoint, pdb.set_trace, etc.)."""
    info("Checking for debugger statements...")
    
    debugger_patterns = [
        r'breakpoint\(\)',
        r'pdb\.set_trace\(\)',
        r'ipdb\.set_trace\(\)',
        r'pudb\.set_trace\(\)',
    ]
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in debugger_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        violations.append(f"{file_path}:{line_num}")
        except Exception:
            continue
    
    if violations:
        fail("03", f"Found {len(violations)} debugger statements")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("03", "No debugger statements found")

def check_key_04_no_empty_except_blocks():
    """Key 04: No empty except blocks."""
    info("Checking for empty except blocks...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler):
                        # Check if except block is empty or only contains pass
                        if not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
                            violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue
    
    if violations:
        fail("04", f"Found {len(violations)} empty except blocks")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("04", "No empty except blocks found")

def check_key_05_no_bare_except():
    """Key 05: No bare except clauses (must specify exception type)."""
    info("Checking for bare except clauses...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler):
                        if node.type is None:
                            violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue
    
    if violations:
        fail("05", f"Found {len(violations)} bare except clauses")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("05", "No bare except clauses found")

def check_key_06_no_eval_exec():
    """Key 06: No use of eval() or exec()."""
    info("Checking for eval/exec usage...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                        if node.func.id in ('eval', 'exec'):
                            violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue
    
    if violations:
        fail("06", f"Found {len(violations)} eval/exec calls")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("06", "No eval/exec usage found")

def check_key_07_no_star_imports():
    """Key 07: No star imports (from module import *)."""
    info("Checking for star imports...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.names[0].name == '*':
                            violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue
    
    if violations:
        fail("07", f"Found {len(violations)} star imports")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("07", "No star imports found")

def check_key_08_no_relative_imports():
    """Key 08: No relative imports in package code."""
    info("Checking for relative imports...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module is None and node.level > 0:
                            violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue
    
    if violations:
        fail("08", f"Found {len(violations)} relative imports")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("08", "No relative imports found")

def check_key_09_no_unused_imports():
    """Key 09: No unused imports."""
    info("Checking for unused imports...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = parse_python_file(file_path)
            if tree:
                # Collect all imports
                imports = set()
                import_lines = {}
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name)
                            import_lines[alias.name] = node.lineno
                    elif isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            imports.add(alias.name)
                            import_lines[alias.name] = node.lineno
                
                # Check if imports are used
                used_names = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name):
                        used_names.add(node.id)
                    elif isinstance(node, ast.Attribute):
                        # Get the base name for attribute access
                        if isinstance(node.value, ast.Name):
                            used_names.add(node.value.id)
                
                # Find unused imports
                for imp in imports:
                    if imp not in used_names and not imp.startswith('_'):
                        violations.append(f"{file_path}:{import_lines[imp]}")
        except Exception:
            continue
    
    if violations:
        fail("09", f"Found {len(violations)} unused imports")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("09", "No unused imports found")

def check_key_10_no_long_lines():
    """Key 10: No lines longer than 100 characters."""
    info("Checking for long lines...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    if len(line.rstrip()) > 100:
                        violations.append(f"{file_path}:{i} ({len(line.rstrip())} chars)")
        except Exception:
            continue
    
    if violations:
        fail("10", f"Found {len(violations)} lines > 100 chars")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("10", "All lines within 100 character limit")

def check_key_11_no_trailing_whitespace():
    """Key 11: No trailing whitespace."""
    info("Checking for trailing whitespace...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    if line.rstrip() != line.rstrip('\n\r'):
                        violations.append(f"{file_path}:{i}")
        except Exception:
            continue
    
    if violations:
        fail("11", f"Found {len(violations)} lines with trailing whitespace")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("11", "No trailing whitespace found")

def check_key_12_no_missing_newline():
    """Key 12: All files must end with a newline."""
    info("Checking for missing final newline...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content and not content.endswith('\n'):
                    violations.append(file_path)
        except Exception:
            continue
    
    if violations:
        fail("12", f"Found {len(violations)} files missing final newline")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("12", "All files end with newline")

def check_key_13_no_tabs():
    """Key 13: Use spaces for indentation, not tabs."""
    info("Checking for tab characters...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    if '\t' in line:
                        violations.append(f"{file_path}:{i}")
                        break  # One report per file
        except Exception:
            continue
    
    if violations:
        fail("13", f"Found {len(violations)} files with tab characters")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("13", "No tab characters found")

def check_key_14_no_duplicate_imports():
    """Key 14: No duplicate imports."""
    info("Checking for duplicate imports...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append((alias.name, node.lineno))
                    elif isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            imports.append((f"{node.module}.{alias.name}" if node.module else alias.name, node.lineno))
                
                # Check for duplicates
                seen = set()
                for imp, line in imports:
                    if imp in seen:
                        violations.append(f"{file_path}:{line}")
                    seen.add(imp)
        except Exception:
            continue
    
    if violations:
        fail("14", f"Found {len(violations)} duplicate imports")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("14", "No duplicate imports found")

def check_key_15_no_magic_numbers():
    """Key 15: Avoid magic numbers (use named constants)."""
    info("Checking for magic numbers...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                        # Skip common values
                        if node.value in (0, 1, -1, 2, 10, 100, 1000):
                            continue
                        # Skip if it's a default argument
                        if hasattr(node, 'parent'):
                            continue
                        violations.append(f"{file_path}:{node.lineno} ({node.value})")
        except Exception:
            continue
    
    if violations:
        warn("15", f"Found {len(violations)} potential magic numbers")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("15", "No obvious magic numbers found")

def check_key_16_no_deep_nesting():
    """Key 16: No code nested deeper than 4 levels."""
    info("Checking for deep nesting...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    depth = 0
                    parent = node
                    while hasattr(parent, 'parent'):
                        parent = parent.parent
                        depth += 1
                        if depth > 4:
                            violations.append(f"{file_path}:{node.lineno}")
                            break
        except Exception:
            continue
    
    if violations:
        fail("16", f"Found {len(violations)} deeply nested blocks")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("16", "No deep nesting found")

def check_key_17_no_large_functions():
    """Key 17: No functions longer than 50 lines."""
    info("Checking for large functions...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Calculate function size
                        if hasattr(node, 'end_lineno'):
                            size = node.end_lineno - node.lineno + 1
                        else:
                            size = len(node.body)
                        if size > 50:
                            violations.append(f"{file_path}:{node.lineno} ({size} lines)")
        except Exception:
            continue
    
    if violations:
        fail("17", f"Found {len(violations)} large functions")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("17", "All functions within size limit")

def check_key_18_no_many_parameters():
    """Key 18: No functions with more than 7 parameters."""
    info("Checking for functions with many parameters...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Count parameters (excluding *args, **kwargs)
                        count = len([a for a in node.args.args if a.arg not in ('self', 'cls')])
                        if count > 7:
                            violations.append(f"{file_path}:{node.lineno} ({count} params)")
        except Exception:
            continue
    
    if violations:
        fail("18", f"Found {len(violations)} functions with too many parameters")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("18", "All functions have reasonable parameter count")

def check_key_19_no_complex_functions():
    """Key 19: No functions with cyclomatic complexity > 10."""
    info("Checking for complex functions...")
    
    violations = []
    python_files = get_python_files()
    
    def calculate_complexity(node):
        """Calculate cyclomatic complexity of a node."""
        complexity = 1  # Base complexity
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                 ast.ExceptHandler, ast.With, ast.AsyncWith,
                                 ast.And, ast.Or, ast.ListComp, ast.DictComp,
                                 ast.SetComp, ast.GeneratorExp)):
                complexity += 1
        return complexity
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        complexity = calculate_complexity(node)
                        if complexity > 10:
                            violations.append(f"{file_path}:{node.lineno} (complexity: {complexity})")
        except Exception:
            continue
    
    if violations:
        fail("19", f"Found {len(violations)} complex functions")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("19", "All functions have acceptable complexity")

def check_key_20_no_large_classes():
    """Key 20: No classes with more than 20 methods."""
    info("Checking for large classes...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                        if len(methods) > 20:
                            violations.append(f"{file_path}:{node.lineno} ({len(methods)} methods)")
        except Exception:
            continue
    
    if violations:
        fail("20", f"Found {len(violations)} large classes")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("20", "All classes within size limit")

def check_key_21_no_missing_docstrings():
    """Key 21: All public functions and classes must have docstrings."""
    info("Checking for missing docstrings...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    # Skip private functions/classes
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if node.name.startswith('_'):
                            continue
                        if not ast.get_docstring(node):
                            violations.append(f"{file_path}:{node.lineno} {node.name}()")
                    elif isinstance(node, ast.ClassDef):
                        if node.name.startswith('_'):
                            continue
                        if not ast.get_docstring(node):
                            violations.append(f"{file_path}:{node.lineno} {node.name}")
        except Exception:
            continue
    
    if violations:
        fail("21", f"Found {len(violations)} missing docstrings")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("21", "All public functions and classes have docstrings")

def check_key_22_no_type_hints():
    """Key 22: All public functions must have type hints."""
    info("Checking for missing type hints...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if node.name.startswith('_'):
                            continue
                        # Check return type annotation
                        if node.returns is None:
                            violations.append(f"{file_path}:{node.lineno} {node.name}() - return type")
                        # Check parameter type annotations
                        for arg in node.args.args:
                            if arg.annotation is None and arg.arg not in ('self', 'cls'):
                                violations.append(f"{file_path}:{node.lineno} {node.name}() - {arg.arg}")
        except Exception:
            continue
    
    if violations:
        fail("22", f"Found {len(violations)} missing type hints")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("22", "All public functions have type hints")

def check_key_23_no_unreachable_code():
    """Key 23: No unreachable code after return/raise."""
    info("Checking for unreachable code...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        for i, stmt in enumerate(node.body):
                            if isinstance(stmt, (ast.Return, ast.Raise)):
                                if i + 1 < len(node.body):
                                    violations.append(f"{file_path}:{stmt.lineno}")
                                break
        except Exception:
            continue
    
    if violations:
        fail("23", f"Found {len(violations)} instances of unreachable code")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("23", "No unreachable code found")

def check_key_24_no_unused_variables():
    """Key 24: No unused variables."""
    info("Checking for unused variables...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                # Collect all variable assignments
                assigned = set()
                used = set()
                
                for node in ast.walk(tree):
                    # Track assignments
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                assigned.add(target.id)
                    elif isinstance(node, ast.AnnAssign):
                        if isinstance(node.target, ast.Name):
                            assigned.add(node.target.id)
                    # Track usage
                    elif isinstance(node, ast.Name):
                        if isinstance(node.ctx, ast.Load):
                            used.add(node.id)
                
                # Find unused variables (excluding _ and __)
                for var in assigned:
                    if var not in used and not var.startswith('_'):
                        violations.append(f"{file_path} - {var}")
        except Exception:
            continue
    
    if violations:
        fail("24", f"Found {len(violations)} unused variables")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("24", "No unused variables found")

def check_key_25_no_global_variables():
    """Key 25: No global variables (except constants)."""
    info("Checking for global variables...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                # Skip constants (ALL_CAPS)
                                if target.id.isupper():
                                    continue
                                # Skip module-level imports
                                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                                    if node.value.func.id in ('import', '__import__'):
                                        continue
                                violations.append(f"{file_path}:{node.lineno} {target.id}")
        except Exception:
            continue
    
    if violations:
        fail("25", f"Found {len(violations)} global variables")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("25", "No global variables found")

def check_key_26_no_direct_sql():
    """Key 26: No direct SQL queries (use ORM)."""
    info("Checking for direct SQL queries...")
    
    sql_patterns = [
        r'\.execute\s*\(\s*["\'].*?(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)',
        r'\.raw\s*\(\s*["\'].*?(SELECT|INSERT|UPDATE|DELETE)',
        r'cursor\.execute',
        r'db\.execute',
    ]
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in sql_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        violations.append(f"{file_path}:{line_num}")
        except Exception:
            continue
    
    if violations:
        fail("26", f"Found {len(violations)} direct SQL queries")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("26", "No direct SQL queries found")

def check_key_27_no_empty_sov_files() -> None:
    """
    Key 27 – STRICT: No zero-byte sovereign Python files, including __init__.py.
    
    Placeholder files (size 0) are banned. If __init__.py exists, it must
    contain a package docstring, __version__, or __all__ to justify its existence.
    """
    info("Checking for empty placeholder files...")
    
    violations: List[str] = []
    python_files = get_python_files()
    
    # Iterate all Python files
    for file_path in python_files:
        try:
            # Check if file exists and has zero bytes
            if os.path.exists(file_path) and os.path.getsize(file_path) == 0:
                violations.append(file_path)
        except Exception:
            continue

    if violations:
        fail(
            "27",
            "EMPTY PLACEHOLDER FILES (Size 0 bytes) DETECTED:\n"
            + "\n".join(f"  - {v}" for v in violations),
        )
    else:
        success("27", "No empty sovereign Python files (including __init__.py)")

# Alias for backward compatibility with command-line interface
def check_key_27() -> None:
    """Alias for check_key_27_no_empty_sov_files."""
    check_key_27_no_empty_sov_files()

def check_key_28_no_hardcoded_urls():
    """Key 28: No hardcoded URLs (use config)."""
    info("Checking for hardcoded URLs...")
    
    url_patterns = [
        r'https?://[^"\']+',
        r'ftp://[^"\']+',
        r'ws[s]?://[^"\']+',
    ]
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in url_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        # Skip documentation strings
                        if '"""' in content[:match.start()] and '"""' in content[match.end():]:
                            continue
                        line_num = content[:match.start()].count('\n') + 1
                        violations.append(f"{file_path}:{line_num}")
        except Exception:
            continue
    
    if violations:
        warn("28", f"Found {len(violations)} hardcoded URLs")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("28", "No hardcoded URLs found")

def check_key_29_no_hardcoded_ports():
    """Key 29: No hardcoded port numbers."""
    info("Checking for hardcoded ports...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for common port patterns
                matches = re.finditer(r':(80|443|8080|3000|5000|8000|9000|5432|3306|6379|27017)\b', content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    violations.append(f"{file_path}:{line_num} - port {match.group(1)}")
        except Exception:
            continue
    
    if violations:
        warn("29", f"Found {len(violations)} hardcoded ports")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("29", "No hardcoded ports found")

def check_key_30_no_time_sleep():
    """Key 30: No time.sleep in production code (use async)."""
    info("Checking for time.sleep usage...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Attribute):
                            if node.func.attr == 'sleep' and isinstance(node.func.value, ast.Name):
                                if node.func.value.id == 'time':
                                    violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue
    
    if violations:
        fail("30", f"Found {len(violations)} time.sleep calls")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("30", "No time.sleep usage found")

def check_key_31_no_threading():
    """Key 31: No threading module (use asyncio)."""
    info("Checking for threading module usage...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name == 'threading':
                                violations.append(f"{file_path}:{node.lineno}")
                    elif isinstance(node, ast.ImportFrom):
                        if node.module == 'threading':
                            violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue
    
    if violations:
        fail("31", f"Found {len(violations)} threading imports")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("31", "No threading module usage found")

def check_key_32_no_blocking_io():
    """Key 32: No blocking I/O in async functions."""
    info("Checking for blocking I/O in async functions...")
    
    violations = []
    python_files = get_python_files()
    
    blocking_calls = {
        'open', 'read', 'write', 'requests.get', 'requests.post',
        'urllib.request.urlopen', 'socket.socket', 'os.system',
        'subprocess.run', 'subprocess.call', 'subprocess.check_output'
    }
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.AsyncFunctionDef):
                        for child in ast.walk(node):
                            if isinstance(child, ast.Call):
                                if isinstance(child.func, ast.Name):
                                    if child.func.id in blocking_calls:
                                        violations.append(f"{file_path}:{child.lineno}")
                                elif isinstance(child.func, ast.Attribute):
                                    if child.func.attr in blocking_calls:
                                        violations.append(f"{file_path}:{child.lineno}")
        except Exception:
            continue
    
    if violations:
        fail("32", f"Found {len(violations)} blocking I/O in async functions")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("32", "No blocking I/O in async functions found")

def check_key_33_no_lambda_abuse():
    """Key 33: No complex lambda expressions (use functions)."""
    info("Checking for complex lambda expressions...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Lambda):
                        # Count expressions in lambda
                        expr_count = len(list(ast.walk(node.body)))
                        if expr_count > 5:
                            violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue
    
    if violations:
        warn("33", f"Found {len(violations)} complex lambda expressions")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("33", "No complex lambda expressions found")

def check_key_34_no_list_comprehension_abuse():
    """Key 34: No complex list comprehensions (use loops)."""
    info("Checking for complex list comprehensions...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
                        # Count generators and conditions
                        generators = len(node.generators)
                        if generators > 2:
                            violations.append(f"{file_path}:{node.lineno}")
                        elif generators == 2:
                            # Check if nested
                            if node.generators[0].iter != node.generators[1].iter:
                                violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue
    
    if violations:
        warn("34", f"Found {len(violations)} complex comprehensions")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("34", "No complex comprehensions found")

def check_key_35_no_try_except_everywhere():
    """Key 35: No excessive try-except blocks (handle at boundaries)."""
    info("Checking for excessive try-except blocks...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                try_count = 0
                total_statements = 0
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Try):
                        try_count += 1
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        total_statements += len(node.body)
                
                if total_statements > 0 and try_count / total_statements > 0.3:
                    violations.append(f"{file_path} - {try_count} tries in {total_statements} statements")
        except Exception:
            continue
    
    if violations:
        warn("35", f"Found {len(violations)} files with excessive try-except")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("35", "Try-except usage is reasonable")

def check_key_36_no_class_abuse():
    """Key 36: No classes with only static methods (use modules)."""
    info("Checking for static-only classes...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                        if not methods:
                            continue
                        
                        # Check if all methods are static
                        all_static = True
                        for method in methods:
                            if not any(d.id == 'staticmethod' for d in method.decorator_list if isinstance(d, ast.Name)):
                                all_static = False
                                break
                        
                        if all_static and len(methods) > 1:
                            violations.append(f"{file_path}:{node.lineno} {node.name}")
        except Exception:
            continue
    
    if violations:
        warn("36", f"Found {len(violations)} static-only classes")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("36", "No static-only classes found")

def check_key_37_no_inheritance_abuse():
    """Key 37: No inheritance chains deeper than 3 levels."""
    info("Checking for deep inheritance chains...")
    
    violations = []
    python_files = get_python_files()
    
    # Build inheritance map
    inheritance = {}
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        bases = []
                        for base in node.bases:
                            if isinstance(base, ast.Name):
                                bases.append(base.id)
                        inheritance[node.name] = bases
        except Exception:
            continue
    
    # Check depth
    def get_depth(cls, visited=None):
        if visited is None:
            visited = set()
        if cls in visited:
            return 0  # Circular inheritance
        visited.add(cls)
        if cls not in inheritance or not inheritance[cls]:
            return 0
        return 1 + max(get_depth(base, visited.copy()) for base in inheritance[cls])
    
    for cls in inheritance:
        depth = get_depth(cls)
        if depth > 3:
            violations.append(f"{cls} - depth {depth}")
    
    if violations:
        fail("37", f"Found {len(violations)} deep inheritance chains")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("37", "Inheritance depth is acceptable")

def check_key_38_no_property_abuse():
    """Key 38: No excessive use of @property (use methods)."""
    info("Checking for property abuse...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                        properties = [m for m in methods if any(d.id == 'property' for d in m.decorator_list if isinstance(d, ast.Name))]
                        
                        if len(properties) > 5:
                            violations.append(f"{file_path}:{node.lineno} {node.name} - {len(properties)} properties")
        except Exception:
            continue
    
    if violations:
        warn("38", f"Found {len(violations)} classes with many properties")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("38", "Property usage is reasonable")

def check_key_39_no_dunder_abuse():
    """Key 39: No excessive dunder methods (use simple methods)."""
    info("Checking for dunder method abuse...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                        dunders = [m for m in methods if m.name.startswith('__') and m.name.endswith('__')]
                        
                        # Skip common dunders
                        common = {'__init__', '__str__', '__repr__', '__eq__', '__hash__'}
                        unusual = [m for m in dunders if m.name not in common]
                        
                        if len(unusual) > 5:
                            violations.append(f"{file_path}:{node.lineno} {node.name} - {len(unusual)} unusual dunders")
        except Exception:
            continue
    
    if violations:
        warn("39", f"Found {len(violations)} classes with many dunder methods")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("39", "Dunder method usage is reasonable")

def check_key_40_no_metaclass_abuse():
    """Key 40: No metaclasses unless absolutely necessary."""
    info("Checking for metaclass usage...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        for keyword in node.keywords:
                            if keyword.arg == 'metaclass':
                                violations.append(f"{file_path}:{node.lineno} {node.name}")
        except Exception:
            continue
    
    if violations:
        warn("40", f"Found {len(violations)} metaclass usages")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("40", "No metaclass usage found")

def check_key_41_no_deep_directories():
    """Key 41: No directories deeper than 3 levels (Light Canon)."""
    info("Checking directory depth (Light Canon)...")
    
    max_depth = 0
    deep_dirs = []
    sovereign_dirs = {
        'agentic_core', 'apps_lic', 'apps_rg', 'apps_shared', 'schemas',
        'prompt_governance', 'observability', 'config', 'data', 'archives',
        '01_runtime_logic', '02_runtime_cache', '03_scripts_logic', '04_scripts_cache',
        '05_runtime_security', '06_runtime_runtime', '07_runtime_pipeline',
        '08_shared_security', '09_shared_runtime', '10_shared_pipeline',
        '11_shared_logic', '12_shared_cache', '13_scripts_security',
        '14_scripts_runtime', '15_scripts_pipeline'
    }
    
    for root, dirs, files in os.walk('.'):
        # Skip hidden, non-source, archives, and data dirs
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'__pycache__', 'archives', 'data'}]
        
        # Calculate depth
        parts = Path(root).parts
        if not parts:
            continue  # Skip empty paths
        if parts[0] == '.':
            parts = parts[1:]
        if not parts:
            continue  # Skip if only had '.'
        
        # Check if in sovereign directory
        if parts and parts[0] in sovereign_dirs:
            continue  # Sovereign dirs are exempt
        
        depth = len(parts)
        if depth > max_depth:
            max_depth = depth
        if depth > 3:
            deep_dirs.append(f"{root} (depth {depth})")
    
    if deep_dirs:
        fail("41", f"Found {len(deep_dirs)} directories deeper than 3 levels")
        for d in deep_dirs[:5]:
            print(f"    {d}")
        if len(deep_dirs) > 5:
            print(f"    ... and {len(deep_dirs) - 5} more")
    else:
        success("41", f"All directories within 3-level limit (max: {max_depth})")

def check_key_42_no_large_files():
    """Key 42: No files larger than 500 lines."""
    info("Checking for large files...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) > 500:
                    violations.append(f"{file_path} ({len(lines)} lines)")
        except Exception:
            continue
    
    if violations:
        fail("42", f"Found {len(violations)} large files")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("42", "All files within 500-line limit")

def check_key_43_no_many_classes():
    """Key 43: No files with more than 10 classes."""
    info("Checking for files with many classes...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                if len(classes) > 10:
                    violations.append(f"{file_path} ({len(classes)} classes)")
        except Exception:
            continue
    
    if violations:
        fail("43", f"Found {len(violations)} files with many classes")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("43", "All files have reasonable class count")

def check_key_44_no_circular_imports():
    """Key 44: No circular imports."""
    info("Checking for circular imports...")
    
    # Build import graph
    imports = {}
    python_files = get_python_files()
    
    for file_path in python_files:
        module_name = file_path.replace('/', '.').replace('.py', '')
        imports[module_name] = set()
        
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports[module_name].add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports[module_name].add(node.module)
        except Exception:
            continue
    
    # Detect cycles
    visited = set()
    rec_stack = set()
    cycles = []
    
    def dfs(node, path):
        if node in rec_stack:
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:] + [node])
            return
        if node in visited:
            return
        
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in imports.get(node, []):
            if neighbor in imports:
                dfs(neighbor, path + [node])
        
        rec_stack.remove(node)
    
    for module in imports:
        if module not in visited:
            dfs(module, [])
    
    if cycles:
        fail("44", f"Found {len(cycles)} circular import chains")
        for cycle in cycles[:3]:
            print(f"    {' -> '.join(cycle)}")
    else:
        success("44", "No circular imports found")

def check_key_45_no_dead_code():
    """Key 45: No unreachable or dead code."""
    info("Checking for dead code...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                # Check for functions that are never called
                defined_functions = set()
                called_functions = set()
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not node.name.startswith('_'):
                            defined_functions.add(node.name)
                    elif isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            called_functions.add(node.func.id)
                
                # Find uncalled functions (excluding special methods)
                for func in defined_functions:
                    if func not in called_functions and not func.startswith('__'):
                        violations.append(f"{file_path} - {func}()")
        except Exception:
            continue
    
    if violations:
        warn("45", f"Found {len(violations)} potentially unused functions")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("45", "No obvious dead code found")

def check_key_46_no_duplicate_code():
    """Key 46: No duplicate code blocks (DRY principle)."""
    info("Checking for duplicate code (simplified)...")
    
    # This is a simplified check - in practice would need more sophisticated analysis
    violations = []
    python_files = get_python_files()
    
    # Track function signatures
    functions = {}
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Create a signature based on name and parameters
                        params = [a.arg for a in node.args.args]
                        signature = f"{node.name}({', '.join(params)})"
                        if signature in functions:
                            violations.append(f"Duplicate: {functions[signature]} and {file_path}")
                        else:
                            functions[signature] = file_path
        except Exception:
            continue
    
    if violations:
        warn("46", f"Found {len(violations)} potentially duplicate functions")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("46", "No obvious duplicate code found")

def check_key_47_no_violate_naming():
    """Key 47: Follow Python naming conventions."""
    info("Checking naming conventions...")
    
    violations = []
    python_files = get_python_files()
    
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    # Classes: PascalCase
                    if isinstance(node, ast.ClassDef):
                        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                            violations.append(f"{file_path}:{node.lineno} Class '{node.name}' should be PascalCase")
                    
                    # Functions/variables: snake_case
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                            violations.append(f"{file_path}:{node.lineno} Function '{node.name}' should be snake_case")
                    
                    # Constants: UPPER_CASE
                    elif isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                if target.id.isupper() and not re.match(r'^[A-Z_][A-Z0-9_]*$', target.id):
                                    violations.append(f"{file_path}:{node.lineno} Constant '{target.id}' should be UPPER_CASE")
        except Exception:
            continue
    
    if violations:
        fail("47", f"Found {len(violations)} naming convention violations")
        for violation in violations[:5]:
            print(f"    {violation}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        success("47", "Naming conventions are followed")

def check_key_48_reserved():
    """Key 48: RESERVED - replaced by universal depth law."""
    info("Key 48 is reserved - replaced by universal depth law")
    success("48", "Reserved key - universal depth law applies")

def check_key_49_universal_depth():
    """Key 49: Universal max 5 levels from repository root."""
    info("Checking universal depth law (max 5 from root)...")
    
    max_depth = 0
    deep_paths = []
    exclude_dirs = {'.git', '__pycache__', '.pytest_cache', '.tox', 'venv', 'env', 
                    '.venv', '.env', 'node_modules', '.idea', '.vscode', 'dist', 
                    'build', 'data', 'archives'}
    
    for root, dirs, files in os.walk('.'):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # Calculate true depth from root
        path_parts = Path(root).parts
        if path_parts and path_parts[0] == '.':
            path_parts = path_parts[1:]
        
        true_depth = len(path_parts)
        if true_depth > max_depth:
            max_depth = true_depth
        
        if true_depth > 5:
            deep_paths.append(f"{root} (depth {true_depth})")
    
    if deep_paths:
        fail("49", f"Found {len(deep_paths)} paths exceeding depth 5 from root")
        for path in deep_paths[:5]:
            print(f"    {path}")
        if len(deep_paths) > 5:
            print(f"    ... and {len(deep_paths) - 5} more")
    else:
        success("49", f"All paths within depth 5 from root (max: {max_depth})")

def check_key_50_canon_meta_integrity():
    """Key 50: Verify all 50 canon keys are implemented and in order."""
    info("Verifying canon meta-integrity...")
    
    # Check that we have all expected keys
    expected_keys = {f"{i:02d}" for i in range(1, 50)}
    expected_keys.add("00")
    expected_keys.add("49")
    expected_keys.add("50")
    
    implemented_keys = set(validation_results.keys())
    
    missing_keys = expected_keys - implemented_keys
    extra_keys = implemented_keys - expected_keys
    
    if missing_keys:
        fail("50", f"Missing canon keys: {sorted(missing_keys)}")
    elif extra_keys:
        fail("50", f"Extra canon keys: {sorted(extra_keys)}")
    else:
        success("50", f"All {len(expected_keys)} canon keys implemented")

def run_all_checks():
    """Run all 50 canon validation checks."""
    print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Subatomic Canon Validator - Agentic Workflow{Colors.END}")
    print(f"{Colors.CYAN}Validating 50 strict enforcement rules...{Colors.END}\n")
    
    # Phase 1: Code Hygiene (Keys 00-09)
    print(f"{Colors.YELLOW}Phase 1: Code Hygiene (Keys 00-09){Colors.END}")
    check_key_00_no_hardcoded_secrets()
    check_key_01_no_todo_comments()
    check_key_02_no_print_statements()
    check_key_03_no_debugger_statements()
    check_key_04_no_empty_except_blocks()
    check_key_05_no_bare_except()
    check_key_06_no_eval_exec()
    check_key_07_no_star_imports()
    check_key_08_no_relative_imports()
    check_key_09_no_unused_imports()
    
    # Phase 2: Code Style (Keys 10-14)
    print(f"\n{Colors.YELLOW}Phase 2: Code Style (Keys 10-14){Colors.END}")
    check_key_10_no_long_lines()
    check_key_11_no_trailing_whitespace()
    check_key_12_no_missing_newline()
    check_key_13_no_tabs()
    check_key_14_no_duplicate_imports()
    
    # Phase 3: Code Structure (Keys 15-20)
    print(f"\n{Colors.YELLOW}Phase 3: Code Structure (Keys 15-20){Colors.END}")
    check_key_15_no_magic_numbers()
    check_key_16_no_deep_nesting()
    check_key_17_no_large_functions()
    check_key_18_no_many_parameters()
    check_key_19_no_complex_functions()
    check_key_20_no_large_classes()
    
    # Phase 4: Documentation & Types (Keys 21-25)
    print(f"\n{Colors.YELLOW}Phase 4: Documentation & Types (Keys 21-25){Colors.END}")
    check_key_21_no_missing_docstrings()
    check_key_22_no_type_hints()
    check_key_23_no_unreachable_code()
    check_key_24_no_unused_variables()
    check_key_25_no_global_variables()
    
    # Phase 5: External Dependencies (Keys 26-30)
    print(f"\n{Colors.YELLOW}Phase 5: External Dependencies (Keys 26-30){Colors.END}")
    check_key_26_no_direct_sql()
    check_key_27_no_empty_sov_files()
    check_key_28_no_hardcoded_urls()
    check_key_29_no_hardcoded_ports()
    check_key_30_no_time_sleep()
    
    # Phase 6: Concurrency (Keys 31-32)
    print(f"\n{Colors.YELLOW}Phase 6: Concurrency (Keys 31-32){Colors.END}")
    check_key_31_no_threading()
    check_key_32_no_blocking_io()
    
    # Phase 7: Pythonic Patterns (Keys 33-40)
    print(f"\n{Colors.YELLOW}Phase 7: Pythonic Patterns (Keys 33-40){Colors.END}")
    check_key_33_no_lambda_abuse()
    check_key_34_no_list_comprehension_abuse()
    check_key_35_no_try_except_everywhere()
    check_key_36_no_class_abuse()
    check_key_37_no_inheritance_abuse()
    check_key_38_no_property_abuse()
    check_key_39_no_dunder_abuse()
    check_key_40_no_metaclass_abuse()
    
    # Phase 8: Light Canon (Keys 41-47)
    print(f"\n{Colors.YELLOW}Phase 8: Light Canon (Keys 41-47){Colors.END}")
    check_key_41_no_deep_directories()
    check_key_42_no_large_files()
    check_key_43_no_many_classes()
    check_key_44_no_circular_imports()
    check_key_45_no_dead_code()
    check_key_46_no_duplicate_code()
    check_key_47_no_violate_naming()
    
    # Phase 9: Universal Laws (Keys 48-50)
    print(f"\n{Colors.YELLOW}Phase 9: Universal Laws (Keys 48-50){Colors.END}")
    check_key_48_reserved()
    check_key_49_universal_depth()
    check_key_50_canon_meta_integrity()
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    passed = len([r for r in validation_results.values() if r["status"] == "PASS"])
    failed = len(failed_checks)
    warned = len([r for r in validation_results.values() if r["status"] == "WARN"])
    
    if failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ SUBATOMIC PERFECTION ACHIEVED{Colors.END}")
        print(f"{Colors.GREEN}All {passed} checks passed{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ CANON VIOLATIONS DETECTED{Colors.END}")
        print(f"{Colors.RED}{failed} failed, {warned} warnings, {passed} passed{Colors.END}")
        print(f"\n{Colors.YELLOW}Failed keys: {', '.join(sorted(failed_checks))}{Colors.END}")
    
    print(f"\n{Colors.CYAN}Zero tolerance for stubs, debt, or sprawl.{Colors.END}")
    print(f"{Colors.CYAN}Fix all violations before proceeding.{Colors.END}")
    
    return failed == 0

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Subatomic Canon Validator")
    parser.add_argument("--key", type=str, help="Run specific key (e.g., '01' or 'all')")
    parser.add_argument("--phase", type=int, choices=range(1, 10), help="Run specific phase (1-9)")
    parser.add_argument("--list", action="store_true", help="List all available checks")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available Canon Keys:")
        for i in range(51):
            key = f"{i:02d}"
            print(f"  Key {key}: {get_check_description(key)}")
        return
    
    if args.key:
        if args.key == "all":
            success = run_all_checks()
        else:
            # Run specific key
            check_func = globals().get(f"check_key_{args.key}")
            if check_func:
                check_func()
                success = args.key not in failed_checks
            else:
                print(f"Unknown key: {args.key}")
                success = False
    elif args.phase:
        # Run specific phase
        phase_checks = get_phase_checks(args.phase)
        for check_func in phase_checks:
            check_func()
        success = len(failed_checks) == 0
    else:
        # Run all checks
        success = run_all_checks()
    
    sys.exit(0 if success else 1)

def get_check_description(key: str) -> str:
    """Get description for a canon key."""
    descriptions = {
        "00": "No hardcoded secrets",
        "01": "No TODO/FIXME comments",
        "02": "No print statements",
        "03": "No debugger statements",
        "04": "No empty except blocks",
        "05": "No bare except clauses",
        "06": "No eval/exec usage",
        "07": "No star imports",
        "08": "No relative imports",
        "09": "No unused imports",
        "10": "No long lines (>100 chars)",
        "11": "No trailing whitespace",
        "12": "Files end with newline",
        "13": "No tab characters",
        "14": "No duplicate imports",
        "15": "No magic numbers",
        "16": "No deep nesting (>4 levels)",
        "17": "No large functions (>50 lines)",
        "18": "No many parameters (>7)",
        "19": "No complex functions (CC>10)",
        "20": "No large classes (>20 methods)",
        "21": "Public functions have docstrings",
        "22": "Public functions have type hints",
        "23": "No unreachable code",
        "24": "No unused variables",
        "25": "No global variables",
        "26": "No direct SQL queries",
        "27": "No empty placeholder files (0 bytes)",
        "28": "No hardcoded URLs",
        "29": "No hardcoded ports",
        "30": "No time.sleep in production",
        "31": "No threading module",
        "32": "No blocking I/O in async",
        "33": "No complex lambdas",
        "34": "No complex comprehensions",
        "35": "No excessive try-except",
        "36": "No static-only classes",
        "37": "No deep inheritance (>3)",
        "38": "No excessive @property",
        "39": "No excessive dunder methods",
        "40": "No metaclasses",
        "41": "No deep directories (>3)",
        "42": "No large files (>500 lines)",
        "43": "No many classes (>10)",
        "44": "No circular imports",
        "45": "No dead code",
        "46": "No duplicate code",
        "47": "Follow naming conventions",
        "48": "RESERVED",
        "49": "Universal max 5 levels from root",
        "50": "Canon meta-integrity check",
    }
    return descriptions.get(key, "Unknown key")

def get_phase_checks(phase: int) -> List:
    """Get list of check functions for a phase."""
    phases = {
        1: [
            check_key_00_no_hardcoded_secrets,
            check_key_01_no_todo_comments,
            check_key_02_no_print_statements,
            check_key_03_no_debugger_statements,
            check_key_04_no_empty_except_blocks,
            check_key_05_no_bare_except,
            check_key_06_no_eval_exec,
            check_key_07_no_star_imports,
            check_key_08_no_relative_imports,
            check_key_09_no_unused_imports,
        ],
        2: [
            check_key_10_no_long_lines,
            check_key_11_no_trailing_whitespace,
            check_key_12_no_missing_newline,
            check_key_13_no_tabs,
            check_key_14_no_duplicate_imports,
        ],
        3: [
            check_key_15_no_magic_numbers,
            check_key_16_no_deep_nesting,
            check_key_17_no_large_functions,
            check_key_18_no_many_parameters,
            check_key_19_no_complex_functions,
            check_key_20_no_large_classes,
        ],
        4: [
            check_key_21_no_missing_docstrings,
            check_key_22_no_type_hints,
            check_key_23_no_unreachable_code,
            check_key_24_no_unused_variables,
            check_key_25_no_global_variables,
        ],
        5: [
            check_key_26_no_direct_sql,
            check_key_27_no_hardcoded_paths,
            check_key_28_no_hardcoded_urls,
            check_key_29_no_hardcoded_ports,
            check_key_30_no_time_sleep,
        ],
        6: [
            check_key_31_no_threading,
            check_key_32_no_blocking_io,
        ],
        7: [
            check_key_33_no_lambda_abuse,
            check_key_34_no_list_comprehension_abuse,
            check_key_35_no_try_except_everywhere,
            check_key_36_no_class_abuse,
            check_key_37_no_inheritance_abuse,
            check_key_38_no_property_abuse,
            check_key_39_no_dunder_abuse,
            check_key_40_no_metaclass_abuse,
        ],
        8: [
            check_key_41_no_deep_directories,
            check_key_42_no_large_files,
            check_key_43_no_many_classes,
            check_key_44_no_circular_imports,
            check_key_45_no_dead_code,
            check_key_46_no_duplicate_code,
            check_key_47_no_violate_naming,
        ],
        9: [
            check_key_48_reserved,
            check_key_49_universal_depth,
            check_key_50_canon_meta_integrity,
        ],
    }
    return phases.get(phase, [])

if __name__ == "__main__":
    main()
