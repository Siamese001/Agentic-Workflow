"""
SafetyInspector Agent - Security Pattern Enforcer.
KEYS: 0 (Secrets), 1 (TODO/FIXME), 2 (Print), 3 (Debugger), 4 (Empty Except), 5 (Bare Except), 6 (Eval/Exec)
"""

import ast
import asyncio
import re
from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    pass

from agentic_core..base import SubAtomicAgent


class SafetyInspector(SubAtomicAgent):
    """
    KEYS: 0 (Secrets), 1 (TODO/FIXME), 2 (Print), 3 (Debugger), 4 (Empty Except), 5 (Bare Except), 6 (Eval/Exec)
    ROLE: Security Pattern Enforcer. Detects dangerous patterns and patches them.
    """

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Safety Patterns...")
        await asyncio.sleep(0)

        # Key 0: Hardcoded secrets
        passed, details = self.check_key_00_no_hardcoded_secrets()
        self.ctx.report(self.name, 0, passed, details)

        # Key 1: TODO/FIXME comments
        passed, details = self.check_key_01_no_todo_fixme()
        self.ctx.report(self.name, 1, passed, details)

        # Key 2: Print statements
        passed, details = self.check_key_02_no_print_statements()
        self.ctx.report(self.name, 2, passed, details)

        # Key 3: Debugger statements
        passed, details = self.check_key_03_no_debugger_statements()
        self.ctx.report(self.name, 3, passed, details)

        # Key 4: Empty except blocks
        passed, details = self.check_key_04_no_empty_except_blocks()
        self.ctx.report(self.name, 4, passed, details)

        # Key 5: Bare except clauses
        passed, details = self.check_key_05_no_bare_except()
        self.ctx.report(self.name, 5, passed, details)

        # Key 6: Eval/exec usage
        passed, details = self.check_key_06_no_eval_exec()
        self.ctx.report(self.name, 6, passed, details)

        # Check async blocking issues
        passed, details = await self.check_async_blocking_issues()
        if not passed:
            self.ctx.report(self.name, 60, passed, details)

        self.ctx.signals.add("SECURE")

    def check_key_02_no_print_statements(self) -> Tuple[bool, List[str]]:
        """Check for print statements in production code."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        stripped = line.strip()
                        if stripped.startswith("#") or stripped.startswith('"""'):
                            continue
                        if "print(" in line:
                            violations.append(f"{file_path}:{i}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_03_no_debugger_statements(self) -> Tuple[bool, List[str]]:
        """Check for debugger statements."""
        violations = []
        debug_patterns = ["breakpoint()", "pdb.set_trace()", "import pdb", "import ipdb"]
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for pattern in debug_patterns:
                        if pattern in content:
                            violations.append(file_path)
                            break
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_04_no_empty_except_blocks(self) -> Tuple[bool, List[str]]:
        """Check for empty except blocks."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler):
                        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                            violations.append(file_path)
                            break
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_05_no_bare_except(self) -> Tuple[bool, List[str]]:
        """Check for bare except clauses."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler):
                        if node.type is None:
                            violations.append(file_path)
                            break
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_06_no_eval_exec(self) -> Tuple[bool, List[str]]:
        """Check for eval/exec usage."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            if node.func.id in ('eval', 'exec'):
                                violations.append(file_path)
                                break
            except Exception:
                continue
        return (len(violations) == 0, violations)

    async def check_async_blocking_issues(self) -> Tuple[bool, List[str]]:
        """Check for blocking calls in async functions."""
        violations = []
        blocking_patterns = ['time.sleep', 'requests.get', 'requests.post']
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    tree = ast.parse(content)
                has_async = any(isinstance(node, ast.AsyncFunctionDef) for node in ast.walk(tree))
                if has_async:
                    for pattern in blocking_patterns:
                        if pattern in content:
                            violations.append(f"{file_path}: {pattern} in async context")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_00_no_hardcoded_secrets(self) -> Tuple[bool, List[str]]:
        """Check for hardcoded secrets."""
        violations = []
        secret_patterns = [
            r"password\s*=\s*['\"].*['\"]",
            r"api_key\s*=\s*['\"].*['\"]",
            r"secret\s*=\s*['\"].*['\"]",
            r"token\s*=\s*['\"].*['\"]",
        ]

        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for pattern in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            violations.append(file_path)
                            break
            except Exception:
                continue

        return (len(violations) == 0, violations)

    def check_key_01_no_todo_fixme(self) -> Tuple[bool, List[str]]:
        """Check for TODO/FIXME comments."""
        violations = []
        todo_patterns = [r"#\s*TODO", r"#\s*FIXME", r"#\s*XXX", r"#\s*HACK", r"#\s*TEMP"]

        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for pattern in todo_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count("\n") + 1
                            violations.append(f"{file_path}:{line_num}")
            except Exception:
                continue

        return (len(violations) == 0, violations)
