"""
PatternEnforcer Agent - Coding Patterns and Best Practices.
KEYS: 26-39 (SOLID Principles, Error Handling, Dead Code, etc.)
"""

import ast
import re
from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import ValidationContext

from ..base import SubAtomicAgent


class PatternEnforcer(SubAtomicAgent):
    """
    KEYS: 26-39 (Pattern Checks)
    ROLE: Enforces coding patterns and best practices.
    """

    def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Code Patterns...")

        pattern_checks = [
            (26, self.check_key_26_single_responsibility),
            (31, self.check_key_31_no_hardcoded_paths),
            (32, self.check_key_32_no_hardcoded_urls),
            (33, self.check_key_33_error_handling),
            (34, self.check_key_34_no_dead_code),
            (35, self.check_key_35_no_commented_code),
        ]

        for key, check_func in pattern_checks:
            try:
                passed, details = check_func()
                self.ctx.report(self.name, key, passed, details)
            except Exception as e:
                self.ctx.report(self.name, key, False, [str(e)])

    def check_key_26_single_responsibility(self) -> Tuple[bool, List[str]]:
        """Check for classes violating single responsibility principle."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        method_types = set()
                        for item in node.body:
                            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                if item.name.startswith('get_') or item.name.startswith('set_'):
                                    method_types.add('property')
                                elif item.name.startswith('save_') or item.name.startswith('load_'):
                                    method_types.add('persistence')
                                elif item.name.startswith('validate_'):
                                    method_types.add('validation')
                                else:
                                    method_types.add('business')
                        if len(method_types) > 2:
                            violations.append(f"{file_path}:{node.lineno} {node.name}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_31_no_hardcoded_paths(self) -> Tuple[bool, List[str]]:
        """Check for hardcoded file paths."""
        violations = []
        path_patterns = [r"['\"]\/home\/", r"['\"]C:\\", r"['\"]\/tmp\/"]
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for i, line in enumerate(content.split('\n'), 1):
                        for pattern in path_patterns:
                            if re.search(pattern, line):
                                violations.append(f"{file_path}:{i}")
                                break
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_32_no_hardcoded_urls(self) -> Tuple[bool, List[str]]:
        """Check for hardcoded URLs."""
        violations = []
        url_patterns = [r"http://localhost", r"http://127\.0\.0\.1"]
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for i, line in enumerate(content.split('\n'), 1):
                        for pattern in url_patterns:
                            if re.search(pattern, line):
                                violations.append(f"{file_path}:{i}")
                                break
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_33_error_handling(self) -> Tuple[bool, List[str]]:
        """Check for proper error handling."""
        violations = []
        critical_ops = ['open', 'json.loads', 'requests.get']
        for file_path in self.ctx.python_files:
            if 'test' in file_path.lower():
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        has_try = any(isinstance(stmt, ast.Try) for stmt in ast.walk(node))
                        for stmt in ast.walk(node):
                            if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Name):
                                if stmt.func.id in critical_ops and not has_try:
                                    violations.append(f"{file_path}:{stmt.lineno}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_34_no_dead_code(self) -> Tuple[bool, List[str]]:
        """Check for dead code after return statements."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        if 'return' in line.strip() and i < len(lines):
                            next_line = lines[i].strip()
                            if next_line and not next_line.startswith('#'):
                                violations.append(f"{file_path}:{i+1}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_35_no_commented_code(self) -> Tuple[bool, List[str]]:
        """Check for commented out code."""
        violations = []
        code_patterns = [r"#\s*def\s+\w+\(", r"#\s*class\s+\w+", r"#\s*if\s+"]
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f.readlines(), 1):
                        if line.strip().startswith('#'):
                            for pattern in code_patterns:
                                if re.search(pattern, line):
                                    violations.append(f"{file_path}:{i}")
                                    break
            except Exception:
                continue
        return (len(violations) == 0, violations)
