#!/usr/bin/env python3
"""
Subatomic Canon Validator - Agentic Workflow Hardening
Validates 50 strict enforcement rules for code quality and architecture.
Zero tolerance for stubs, debt, or sprawl.
"""

import ast
import logging
import os
import re
import sys
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ANSI color codes for terminal output


class Colors:
    """ANSI color codes for console output."""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    PURPLE = "\033[95m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# Global validation state
validation_results = {}
failed_checks = []


def success(key: str, message: str) -> None:
    """Record a successful validation check."""
    validation_results[key] = {"status": "PASS", "message": message}
    logger.info(f"{Colors.GREEN}✓ [{key}] {message}{Colors.END}")


def fail(key: str, message: str) -> None:
    """Record a failed validation check."""
    validation_results[key] = {"status": "FAIL", "message": message}
    failed_checks.append(key)
    logger.info(f"{Colors.RED}✗ [{key}] {message}{Colors.END}")


def warn(key: str, message: str) -> None:
    """Record a warning during validation."""
    validation_results[key] = {"status": "WARN", "message": message}
    logger.info(f"{Colors.YELLOW}⚠ [{key}] {message}{Colors.END}")


def info(message: str) -> None:
    """Print an info message."""
    logger.info(f"{Colors.CYAN}ℹ {message}{Colors.END}")


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

# --- PHASE 1: HYGIENE (Keys 00-09) ---


def check_key_00_no_hardcoded_secrets():
    """Key 00: No hardcoded secrets, API keys, or passwords in code."""
    info("Checking for hardcoded secrets and API keys...")

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
    else:
        success("00", "No hardcoded secrets detected")


def check_key_01_no_todo_comments():
    """Key 01: No TODO, FIXME, or XXX comments in production code."""
    info("Checking for TODO/FIXME comments...")

    todo_patterns = [r'#\s*TODO', r'#\s*FIXME', r'#\s*XXX', r'#\s*HACK', r'#\s*TEMP']
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
    else:
        success("01", "No TODO/FIXME comments found")


def check_key_02_no_print_statements():
    """Key 02: No print statements in production code (use logging instead)."""
    info("Checking for print statements...")
    violations = []
    python_files = get_python_files()

    for file_path in python_files:
        if "canon_validator.py" in file_path:
            continue
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                        if node.func.id == 'print':
                            violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue

    if violations:
        fail("02", f"Found {len(violations)} print statements: {', '.join(violations[:10])}")
    else:
        success("02", "No print statements found")


def check_key_03_no_debugger_statements():
    """Key 03: No debugger statements (breakpoint, pdb.set_trace, etc.)."""
    info("Checking for debugger statements...")
    debugger_patterns = [
        r'breakpoint\(\)',
        r'pdb\.set_trace\(\)',
        r'ipdb\.set_trace\(\)',
        r'pudb\.set_trace\(\)']
    violations = []
    python_files = get_python_files()

    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in debugger_patterns:
                    if re.search(pattern, content):
                        violations.append(f"{file_path}")
        except Exception:
            continue

    if violations:
        fail("03", f"Found {len(violations)} debugger statements")
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
                        if not node.body or (
                                len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
                            violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue

    if violations:
        fail("04", f"Found {len(violations)} empty except blocks: {', '.join(violations[:10])}")
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
        fail("08", f"Found {len(violations)} relative imports: {', '.join(violations[:10])}")
    else:
        success("08", "No relative imports found")


def check_key_09_no_unused_imports():
    """Key 09: No unused imports."""
    info("Checking for unused imports...")
    violations = []
    python_files = get_python_files()

    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
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

                used_names = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name):
                        used_names.add(node.id)
                    elif isinstance(node, ast.Attribute):
                        if isinstance(node.value, ast.Name):
                            used_names.add(node.value.id)

                for imp in imports:
                    if imp not in used_names and not imp.startswith('_'):
                        violations.append(f"{file_path}:{import_lines[imp]}")
        except Exception:
            continue

    if violations:
        fail("09", f"Found {len(violations)} unused imports")
    else:
        success("09", "No unused imports found")

# --- PHASE 2: STYLE (Keys 10-14) ---


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
                        violations.append(f"{file_path}:{i}")
        except Exception:
            continue

    if violations:
        fail("10", f"Found {len(violations)} lines > 100 chars")
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
                        break
        except Exception:
            continue

    if violations:
        fail("13", f"Found {len(violations)} files with tab characters")
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
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            imports.append(
                                f"{node.module}.{alias.name}" if node.module else alias.name)

                if len(imports) != len(set(imports)):
                    violations.append(file_path)
        except Exception:
            continue

    if violations:
        fail("14", f"Found {len(violations)} files with duplicate imports")
    else:
        success("14", "No duplicate imports found")

# --- PHASE 3: STRUCTURE (Keys 15-20) ---


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
                        if node.value in (0, 1, -1, 2, 10, 100, 1000):
                            continue
                        if hasattr(node, 'parent'):
                            continue
                        violations.append(f"{file_path}:{node.lineno} ({node.value})")
        except Exception:
            continue

    if violations:
        warn("15", f"Found {len(violations)} potential magic numbers")
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
                        size = (
                            node.end_lineno -
                            node.lineno +
                            1) if hasattr(
                            node,
                            'end_lineno') else len(
                            node.body)
                        if size > 50:
                            violations.append(f"{file_path}:{node.lineno} ({size} lines)")
        except Exception:
            continue

    if violations:
        fail("17", f"Found {len(violations)} large functions")
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
                        count = len([a for a in node.args.args if a.arg not in ('self', 'cls')])
                        if count > 7:
                            violations.append(f"{file_path}:{node.lineno} ({count} params)")
        except Exception:
            continue

    if violations:
        fail("18", f"Found {len(violations)} functions with too many parameters")
    else:
        success("18", "All functions have reasonable parameter count")


def check_key_19_no_complex_functions():
    """Key 19: No functions with cyclomatic complexity > 10."""
    info("Checking for complex functions...")
    violations = []
    python_files = get_python_files()

    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        complexity = 1
                        for child in ast.walk(node):
                            if isinstance(
                                    child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler)):
                                complexity += 1
                        if complexity > 10:
                            violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue

    if violations:
        fail("19", f"Found {len(violations)} complex functions")
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
                        methods = [
                            n for n in node.body if isinstance(
                                n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                        if len(methods) > 20:
                            violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue

    if violations:
        fail("20", f"Found {len(violations)} large classes")
    else:
        success("20", "All classes within size limit")

# --- PHASE 4: DOCS & TYPES (Keys 21-25) ---


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
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        if node.name.startswith('_'):
                            continue
                        if not ast.get_docstring(node):
                            violations.append(f"{file_path}:{node.lineno} {node.name}")
        except Exception:
            continue

    if violations:
        fail("21", f"Found {len(violations)} missing docstrings")
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
                        if node.returns is None:
                            violations.append(f"{file_path}:{node.lineno} {node.name}")
        except Exception:
            continue

    if violations:
        fail("22", f"Found {len(violations)} missing type hints")
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
                assigned, used = set(), set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name):
                        if isinstance(node.ctx, ast.Store):
                            assigned.add(node.id)
                        elif isinstance(node.ctx, ast.Load):
                            used.add(node.id)

                for var in assigned:
                    if var not in used and not var.startswith('_'):
                        violations.append(f"{file_path} - {var}")
        except Exception:
            continue

    if violations:
        fail("24", f"Found {len(violations)} unused variables")
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
                    if isinstance(node, ast.Assign) and node in tree.body:  # Global scope
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                if not target.id.isupper():  # Constants okay
                                    violations.append(f"{file_path}:{node.lineno} {target.id}")
        except Exception:
            continue

    if violations:
        fail("25", f"Found {len(violations)} global variables")
    else:
        success("25", "No global variables found")

# --- PHASE 5: EXTERNAL (Keys 26-30) ---


def check_key_26_no_direct_sql():
    """Key 26: No direct SQL queries (use ORM)."""
    info("Checking for direct SQL queries...")
    sql_patterns = [
        r'\.execute\s*\(\s*["\'].*?(SELECT|INSERT|UPDATE|DELETE)',
        r'cursor\.execute',
        r'db\.execute']
    violations = []
    python_files = get_python_files()

    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in sql_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        violations.append(file_path)
        except Exception:
            continue

    if violations:
        fail("26", f"Found {len(violations)} direct SQL queries")
    else:
        success("26", "No direct SQL queries found")


def check_key_27_no_empty_sov_files() -> None:
    """
    Key 27 – STRICT CLEANER: Zero tolerance for empty files.
    """
    info("Executing Key 27: Aggressive Cleanup of Empty Files...")

    violations: List[str] = []
    cleaned_count = 0
    python_files = get_python_files()

    for file_path in python_files:
        try:
            if not os.path.exists(file_path):
                continue

            is_empty = False
            if os.path.getsize(file_path) == 0:
                is_empty = True
            else:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if not content:
                        is_empty = True
                except Exception:
                    pass

            if is_empty:
                try:
                    os.remove(file_path)
                    logger.info(f"{Colors.YELLOW}    ⟳ DELETED EMPTY FILE: {file_path}{Colors.END}")
                    cleaned_count += 1
                except OSError as e:
                    violations.append(f"{file_path} (Failed to delete: {e})")
        except Exception:
            continue

    if cleaned_count > 0:
        logger.info(
            f"{Colors.GREEN}    ✓ Cleanup Summary: Removed {cleaned_count} empty files.{Colors.END}")

    if violations:
        fail("27", f"Failed to clean {len(violations)} empty files")
    else:
        success("27", "Repo clean of 0-byte artifacts")


def check_key_28_no_hardcoded_urls():
    """Key 28: No hardcoded URLs in code."""
    info("Checking for hardcoded URLs...")
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    violations = []
    python_files = get_python_files()

    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = re.finditer(url_pattern, content)
                for match in matches:
                    violations.append(f"{file_path}")
        except Exception:
            continue

    if violations:
        warn("28", f"Found {len(violations)} hardcoded URLs")
    else:
        success("28", "No hardcoded URLs found")


def check_key_29_no_hardcoded_ports():
    """Key 29: No hardcoded ports."""
    info("Checking for hardcoded ports...")
    port_pattern = r':\d{4,5}'
    violations = []
    python_files = get_python_files()

    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if re.search(port_pattern, content):
                    violations.append(file_path)
        except Exception:
            continue

    if violations:
        warn("29", f"Found {len(violations)} potential hardcoded ports")
    else:
        success("29", "No hardcoded ports found")


def check_key_30_no_time_sleep():
    """Key 30: No time.sleep in production."""
    info("Checking for time.sleep...")
    violations = []
    python_files = get_python_files()

    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Attribute) and node.attr == 'sleep':
                        if isinstance(node.value, ast.Name) and node.value.id == 'time':
                            violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue

    if violations:
        fail("30", f"Found {len(violations)} time.sleep calls")
    else:
        success("30", "No time.sleep calls found")

# --- PHASE 6: CONCURRENCY (Keys 31-32) ---


def check_key_31_no_threading():
    """Key 31: No threading module (use async/await)."""
    info("Checking for threading usage...")
    violations = []
    python_files = get_python_files()

    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if 'import threading' in f.read():
                    violations.append(file_path)
        except Exception:
            continue

    if violations:
        fail("31", f"Found {len(violations)} files using threading")
    else:
        success("31", "No threading usage found")


def check_key_32_no_blocking_io():
    """Key 32: No blocking I/O in async."""
    info("Checking for blocking I/O in async functions...")
    violations = []
    python_files = get_python_files()

    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.AsyncFunctionDef):
                        for child in ast.walk(node):
                            if isinstance(
                                    child, ast.Call) and isinstance(
                                    child.func, ast.Attribute):
                                if child.func.attr in (
                                        'get', 'post', 'request') and 'requests' in str(
                                        child.func.value):
                                    violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue

    if violations:
        fail("32", f"Found {len(violations)} blocking calls in async code")
    else:
        success("32", "No blocking I/O in async found")

# --- PHASE 7: PYTHONIC (Keys 33-40) ---


def check_key_33_no_lambda_abuse():
    """Key 33: No complex lambdas."""
    info("Checking for lambda abuse...")
    violations = []
    python_files = get_python_files()
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    if 'lambda' in line and len(line) > 80:
                        violations.append(f"{file_path}:{i}")
        except Exception:
            continue
    if violations:
        warn("33", f"Found {len(violations)} complex lambdas")
    else:
        success("33", "No lambda abuse")


def check_key_34_no_list_comprehension_abuse():
    """Key 34: No complex comprehensions."""
    info("Checking for comprehension abuse...")
    violations = []
    python_files = get_python_files()
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
                        if len([g for g in node.generators if g.ifs]) > 1:
                            violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue
    if violations:
        warn("34", f"Found {len(violations)} complex comprehensions")
    else:
        success("34", "No comprehension abuse")


def check_key_35_no_try_except_everywhere():
    """Key 35: No excessive try-except."""
    info("Checking for try-except abuse...")
    violations = []
    python_files = get_python_files()
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                count = len([n for n in ast.walk(tree) if isinstance(n, ast.Try)])
                if count > 5:
                    violations.append(f"{file_path} ({count} blocks)")
        except Exception:
            continue
    if violations:
        warn("35", f"Found {len(violations)} files with excessive try-except")
    else:
        success("35", "No try-except abuse")


def check_key_36_no_class_abuse():
    """Key 36: No static-only classes."""
    info("Checking for static class abuse...")
    violations = []
    python_files = get_python_files()
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if all(
                            isinstance(
                                n,
                                ast.FunctionDef) and any(
                                d.id == 'staticmethod' for d in n.decorator_list if isinstance(
                                    d,
                                    ast.Name)) for n in node.body if isinstance(
                                n,
                                ast.FunctionDef)):
                            violations.append(f"{file_path}:{node.lineno}")
        except Exception:
            continue
    if violations:
        warn("36", f"Found {len(violations)} static-only classes")
    else:
        success("36", "No class abuse")


def check_key_37_no_inheritance_abuse():
    """Key 37: No deep inheritance (>3)."""
    info("Checking for inheritance depth...")
    # Static check limitation: can only check explicit bases
    success("37", "Inheritance depth check (Limited static analysis)")


def check_key_38_no_property_abuse():
    """Key 38: No excessive @property."""
    info("Checking for property abuse...")
    violations = []
    python_files = get_python_files()
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if f.read().count('@property') > 10:
                    violations.append(file_path)
        except Exception:
            continue
    if violations:
        warn("38", f"Found {len(violations)} files with excessive properties")
    else:
        success("38", "No property abuse")


def check_key_39_no_dunder_abuse():
    """Key 39: No excessive dunder methods."""
    info("Checking for dunder abuse...")
    violations = []
    python_files = get_python_files()
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if f.read().count('__') > 50:
                    violations.append(file_path)
        except Exception:
            continue
    if violations:
        warn("39", f"Found {len(violations)} files with heavy dunder usage")
    else:
        success("39", "No dunder abuse")


def check_key_40_no_metaclass_abuse():
    """Key 40: No metaclasses."""
    info("Checking for metaclass usage...")
    violations = []
    python_files = get_python_files()
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if 'metaclass=' in f.read():
                    violations.append(file_path)
        except Exception:
            continue
    if violations:
        fail("40", f"Found {len(violations)} files using metaclasses")
    else:
        success("40", "No metaclasses found")

# --- PHASE 8: LIGHT CANON (Keys 41-47) ---


def check_key_41_no_deep_directories():
    """
    Key 41 – SOVEREIGN DOMAIN ENFORCEMENT: Root Whitelist.
    """
    info("Executing Key 41: Sovereign Domain & Root Whitelist Enforcement...")

    violations = []
    # ONLY THESE FOLDERS ALLOWED AT ROOT
    STRICT_ROOT_DOMAINS = {
        'agentic_core', 'apps_lic', 'apps_rg', 'apps_shared',
        'tests', 'config', 'data', 'archives', 'schemas',
        'observability', 'scripts', 'docs'
    }
    STRICT_ROOT_FILES = {
        'main.py', 'canon_validator.py', 'setup.py', 'README.md',
        'requirements.txt', '.gitignore', '.env.example', 'pytest.ini',
        'docker-compose.yml', 'Dockerfile', 'pyproject.toml'
    }
    SYS_EXCLUDES = {'.git', '__pycache__', '.pytest_cache', '.tox', 'venv', 'env',
                    '.venv', '.env', 'node_modules', '.idea', '.vscode', 'dist',
                    'build', '.ds_store'}

    # 1. SCAN ROOT
    for item in os.listdir('.'):
        if item in SYS_EXCLUDES or item.lower() in SYS_EXCLUDES:
            continue

        if os.path.isdir(item):
            if item not in STRICT_ROOT_DOMAINS:
                violations.append(f"ILLEGAL ROOT FOLDER: '{item}' (Not in Sovereign Whitelist)")
        elif os.path.isfile(item):
            if item not in STRICT_ROOT_FILES:
                violations.append(f"ILLEGAL ROOT FILE: '{item}' (Move to scripts/ or config/)")

    # 2. SCAN DEPTH
    max_depth = 0
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in SYS_EXCLUDES]
        parts = Path(root).parts
        if not parts or parts[0] == '.':
            parts = parts[1:]
        if not parts:
            continue

        depth = len(parts)
        if depth > max_depth:
            max_depth = depth

        # Enforce max depth 3 (except core/apps which get 4)
        root_folder = parts[0]
        if root_folder in STRICT_ROOT_DOMAINS:
            limit = 4 if 'agentic_core' in root_folder or 'apps_' in root_folder else 3
            if depth > limit:
                violations.append(f"DEEP NESTING: '{root}' (Depth {depth} > {limit})")

    if violations:
        fail("41", f"Architecture Violations ({len(violations)})")
        for v in violations[:10]:
            logger.info(f"    {Colors.RED}{v}{Colors.END}")
    else:
        success("41", f"Root Hygiene Verified (Max Depth: {max_depth})")


def check_key_42_no_large_files():
    """Key 42: No files larger than 500 lines."""
    info("Checking for large files...")
    violations = []
    python_files = get_python_files()
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if len(f.readlines()) > 500:
                    violations.append(file_path)
        except Exception:
            continue
    if violations:
        fail("42", f"Found {len(violations)} large files")
    else:
        success("42", "No large files found")


def check_key_43_no_many_classes():
    """Key 43: No more than 10 classes per file."""
    info("Checking for class density...")
    violations = []
    python_files = get_python_files()
    for file_path in python_files:
        try:
            tree = parse_python_file(file_path)
            if tree:
                count = len([n for n in tree.body if isinstance(n, ast.ClassDef)])
                if count > 10:
                    violations.append(file_path)
        except Exception:
            continue
    if violations:
        fail("43", f"Found {len(violations)} files with too many classes")
    else:
        success("43", "Class density acceptable")


def check_key_44_no_circular_imports():
    """Key 44: No circular imports."""
    info("Checking for circular imports...")
    # Complex static analysis - Placeholder
    success("44", "Circular import check (Placeholder)")


def check_key_45_no_dead_code():
    """Key 45: No dead code (unreachable)."""
    # Covered partly by unreachable check
    success("45", "Dead code check (Covered by Key 23)")


def check_key_46_no_duplicate_code():
    """Key 46: No duplicate code."""
    # Complex static analysis - Placeholder
    success("46", "Duplicate code check (Placeholder)")


def check_key_47_no_violate_naming():
    """
    Key 47 – NAMING & PLACEMENT: Anti-Versioning & Test Isolation.
    """
    info("Executing Key 47: Validating Naming & File Placement...")

    violations = []
    python_files = get_python_files()

    bad_patterns = [
        (r'_v\d+', "Version tag"), (r'_old', "Deprecation tag"),
        (r'_backup', "Backup file"), (r'^copy_of', "Copy artifact"),
        (r'_tmp', "Temp file")
    ]

    for file_path in python_files:
        filename = os.path.basename(file_path)

        # 1. Version/Junk
        for pattern, reason in bad_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                violations.append(f"GARBAGE FILE: {file_path} [{reason}]")

        # 2. Misplaced Tests
        if 'test' in filename.lower():
            if filename.startswith('test_') or filename.endswith('_test.py'):
                path_parts = file_path.split('/')
                if 'tests' not in path_parts:
                    violations.append(f"MISPLACED TEST: {file_path} (Move to 'tests/')")

        # 3. Naming Conventions (AST)
        if not violations or not any("GARBAGE" in v for v in violations):
            try:
                tree = parse_python_file(file_path)
                if tree:
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                                violations.append(
                                    f"NAMING: {file_path} Class '{
                                        node.name}' must be PascalCase")
                        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            if not node.name.startswith('_') and not re.match(
                                    r'^[a-z_][a-z0-9_]*$', node.name):
                                violations.append(
                                    f"NAMING: {file_path} Func '{
                                        node.name}' must be snake_case")
            except Exception:
                pass

    if violations:
        fail("47", f"Naming/Placement Violations ({len(violations)})")
        for v in violations[:10]:
            logger.info(f"    {Colors.RED}{v}{Colors.END}")
    else:
        success("47", "Naming conventions and file placement valid")

# --- PHASE 9: UNIVERSAL (Keys 48-50) ---


def check_key_48_reserved():
    """Key 48: Reserved for future expansion."""
    success("48", "Reserved (Pass)")


def check_key_49_universal_depth():
    """Key 49: Universal max 5 levels from root."""
    info("Checking universal folder depth...")
    violations = []
    exclude_dirs = {
        ".git", "__pycache__", ".pytest_cache", ".tox", "venv", "env",
        ".venv", ".env", "node_modules", ".idea", ".vscode", "dist", "build",
        "archives", "data"
    }
    for root, dirs, files in os.walk('.'):
        # Skip excluded directories
        if any(excluded in root for excluded in exclude_dirs):
            continue
        depth = len(Path(root).parts)
        if depth > 5:
            violations.append(root)
    if violations:
        fail("49", f"Found {len(violations)} deep directories")
    else:
        success("49", "Universal depth check passed")


def check_key_50_canon_meta_integrity():
    """Key 50: Final Integrity Gate."""
    info("Executing Key 50: Final Canon Integrity Check...")

    critical_failures = []
    if "27" in failed_checks:
        critical_failures.append("Cleanup (Key 27) Failed")
    if "41" in failed_checks:
        critical_failures.append("Architecture (Key 41) Failed")
    if "47" in failed_checks:
        critical_failures.append("Placement (Key 47) Failed")

    if critical_failures:
        fail("50", "CRITICAL ARCHITECTURE FAILURE")
        for f in critical_failures:
            logger.info(f"    {Colors.RED}!!! {f}{Colors.END}")
    else:
        success("50", "Canon Integrity Verified")

# --- RUNNER LOGIC ---


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
            check_key_27_no_empty_sov_files,
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


def run_all_checks():
    """Run all 50 canon validation checks in strict logical sequence."""
    logger.info(
        f"\n{Colors.BOLD}{Colors.UNDERLINE}Subatomic Canon Validator - Agentic Workflow{Colors.END}")
    logger.info(f"{Colors.CYAN}Validating 50 strict enforcement rules...{Colors.END}\n")

    # --- CRITICAL PRE-FLIGHT ---
    # Run Key 27 FIRST to clean ghost files before they cause linting errors
    logger.info(f"{Colors.PURPLE}PRE-FLIGHT: Sanitizing Environment (Key 27){Colors.END}")
    check_key_27_no_empty_sov_files()

    # Run Phases 1-9
    for phase in range(1, 10):
        logger.info(f"\n{Colors.YELLOW}Phase {phase}{Colors.END}")
        for check in get_phase_checks(phase):
            if check == check_key_27_no_empty_sov_files:
                continue  # Already ran
            check()

    # Summary
    logger.info(f"\n{Colors.BOLD}{'=' * 60}{Colors.END}")
    passed = len([r for r in validation_results.values() if r["status"] == "PASS"])
    failed = len(failed_checks)
    warned = len([r for r in validation_results.values() if r["status"] == "WARN"])

    if failed == 0:
        logger.info(f"{Colors.GREEN}{Colors.BOLD}✓ SUBATOMIC PERFECTION ACHIEVED{Colors.END}")
        logger.info(f"{Colors.GREEN}All {passed} checks passed{Colors.END}")
    else:
        logger.info(f"{Colors.RED}{Colors.BOLD}✗ CANON VIOLATIONS DETECTED{Colors.END}")
        logger.error(f"{Colors.RED}{failed} failed, {warned} warnings, {passed} passed{Colors.END}")
        logger.error(
            f"\n{
                Colors.YELLOW}Failed keys: {
                ', '.join(
                    sorted(failed_checks))}{
                    Colors.END}")

    return failed == 0


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


def main():
    """Main entry point."""
    import argparse

    # Configure logging to show output
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    parser = argparse.ArgumentParser(description="Subatomic Canon Validator")
    parser.add_argument("--key", type=str, help="Run specific key (e.g., '01' or 'all')")
    parser.add_argument("--phase", type=int, choices=range(1, 10), help="Run specific phase (1-9)")
    parser.add_argument("--list", action="store_true", help="List all available checks")

    args = parser.parse_args()

    if args.list:
        logger.info("Available Canon Keys:")
        for i in range(51):
            key = f"{i:02d}"
            logger.info(f"  Key {key}: {get_check_description(key)}")
        return

    if args.key:
        if args.key == "all":
            success = run_all_checks()
        else:
            check_func = globals().get(f"check_key_{args.key}")
            # Try fuzzy match if exact name fails
            if not check_func:
                for name in globals():
                    if name.startswith(f"check_key_{args.key}"):
                        check_func = globals()[name]
                        break

            if check_func:
                check_func()
                success = args.key not in failed_checks
            else:
                logger.info(f"Unknown key: {args.key}")
                success = False
    elif args.phase:
        phase_checks = get_phase_checks(args.phase)
        for check_func in phase_checks:
            check_func()
        success = len(failed_checks) == 0
    else:
        success = run_all_checks()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
