from __future__ import annotations

"""
Analysis Operations - AST Parsing, Linting, and Code Quality Tools
Consolidated from core_utils.py and security_utils.py
"""
import ast
import logging
import subprocess
from typing import Any

from agentic_core.utils.security import safe_execute

Logger: Any = logging.getLogger(__name__)

def validate_python_syntax(file_path: str) -> tuple[bool, str | None]:
    """
    Parse a Python file to check for syntax errors without executing it.

    Args:
        file_path: Path to the file to check

    Returns:
        Tuple[bool, Optional[str]]: (True, None) if valid, (False, error_message) if invalid
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            source: Any = f.read()
        ast.parse(source)
        return (True, None)
    except SyntaxError as e:
        error_msg: Any = f'SyntaxError in {file_path}: {e.msg} at line {e.lineno}'
        Logger.error(error_msg)
        return (False, error_msg)
    except Exception as e:
        error_msg: Any = f'Unexpected error validating {file_path}: {str(e)}'
        Logger.error(error_msg)
        return (False, error_msg)

def run_ruff_check(file_path: str, fix: bool=False) -> tuple[int, str, str]:
    """
    Run Ruff linter on a file.

    Args:
        file_path: Path to the file to check
        fix: Whether to apply fixes automatically

    Returns:
        Tuple[int, str, str]: (returncode, stdout, stderr)
    """
    cmd: Any = ['ruff', 'check', file_path]
    if fix:
        cmd.append('--fix')
    try:
        # Use check=False because ruff returns non-zero when violations are found
        result: Any = safe_execute(cmd, capture_output=True, text=True, timeout=30, check=False)
        return (result.returncode, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return (-1, '', 'Ruff check timed out')
    except FileNotFoundError:
        return (-1, '', 'Ruff not installed')
    except Exception as e:
        return (-1, '', str(e))

def run_black_format(file_path: str, check_only: bool=False) -> tuple[int, str, str]:
    """
    Run Black formatter on a file.

    Args:
        file_path: Path to the file to format
        check_only: Only check formatting without modifying

    Returns:
        Tuple[int, str, str]: (returncode, stdout, stderr)
    """
    cmd: Any = ['black', file_path]
    if check_only:
        cmd.append('--check')
    try:
        # Use check=False because black returns non-zero when formatting changes are needed
        result: Any = safe_execute(cmd, capture_output=True, text=True, timeout=30, check=False)
        return (result.returncode, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return (-1, '', 'Black format timed out')
    except FileNotFoundError:
        return (-1, '', 'Black not installed')
    except Exception as e:
        return (-1, '', str(e))

def analyze_ast(file_path: str) -> dict[str, Any]:
    """
    Analyze Python file AST for structural information.

    Args:
        file_path: Path to the file to analyze

    Returns:
        Dict with AST analysis results
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            source: Any = f.read()
        tree: Any = ast.parse(source)
        analysis: Any = {'functions': [], 'classes': [], 'imports': [], 'globals': [], 'complexity': 0}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis['functions'].append({'name': node.name, 'lineno': node.lineno, 'args': [arg.arg for arg in node.args.args], 'is_async': isinstance(node, ast.AsyncFunctionDef)})
            elif isinstance(node, ast.ClassDef):
                analysis['classes'].append({'name': node.name, 'lineno': node.lineno, 'bases': [ast.unparse(base) for base in node.bases]})
            elif isinstance(node, ast.Import | ast.ImportFrom):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append({'module': alias.name, 'alias': alias.asname, 'lineno': node.lineno})
                else:
                    for alias in node.names:
                        analysis['imports'].append({'module': f'{node.module}.{alias.name}' if node.module else alias.name, 'alias': alias.asname, 'lineno': node.lineno})
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        analysis['globals'].append(target.id)
        return analysis
    except Exception as e:
        Logger.error(f'AST analysis failed for {file_path}: {e}')
        return {'error': str(e)}

def count_lines_of_code(file_path: str) -> dict[str, int]:
    """
    Count lines of code, comments, and blank lines.

    Args:
        file_path: Path to the file to analyze

    Returns:
        Dict with line counts
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            lines: Any = f.readlines()
        total: Any = len(lines)
        blank: Any = sum(1 for line in lines if not line.strip())
        comments: Any = sum(1 for line in lines if line.strip().startswith('#'))
        code: Any = total - blank - comments
        return {'total': total, 'code': code, 'comments': comments, 'blank': blank}
    except Exception as e:
        Logger.error(f'Line count failed for {file_path}: {e}')
        return {'error': str(e)}

def detect_security_issues(file_path: str) -> list[dict[str, Any]]:
    """
    Detect common security issues in Python code.

    Args:
        file_path: Path to the file to analyze

    Returns:
        List of detected security issues
    """
    issues: Any = []
    try:
        with open(file_path, encoding='utf-8') as f:
            source: Any = f.read()
        tree: Any = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'eval':
                    issues.append({'type': 'dangerous_function', 'function': 'eval', 'lineno': node.lineno, 'Severity': 'high', 'message': 'Use of eval() is dangerous and should be avoided'})
                elif isinstance(node.func, ast.Name) and node.func.id == 'exec':
                    issues.append({'type': 'dangerous_function', 'function': 'exec', 'lineno': node.lineno, 'Severity': 'high', 'message': 'Use of exec() is dangerous and should be avoided'})
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['run', 'call', 'Popen']:
                        for keyword in node.keywords:
                            if keyword.arg == 'shell' and isinstance(keyword.value, ast.Constant):
                                if keyword.value.value is True:
                                    issues.append({'type': 'shell_injection', 'function': node.func.attr, 'lineno': node.lineno, 'Severity': 'high', 'message': 'subprocess with shell=True is vulnerable to injection'})
        return issues
    except Exception as e:
        Logger.error(f'Security analysis failed for {file_path}: {e}')
        return [{'error': str(e)}]
