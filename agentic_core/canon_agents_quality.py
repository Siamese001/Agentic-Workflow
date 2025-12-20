"""
Canon Validator Quality Agents
SafetyInspector, DocumentationAgent, NamingAgent - Code quality and standards.
"""

import ast
import re
from typing import List, Tuple

from agentic_core.canon_base_agent import SubAtomicAgent


class SafetyInspector(SubAtomicAgent):
    """
    KEYS: 0 (Secrets), 1 (TODO/FIXME), 2 (Print), 3 (Debugger), 4 (Empty Except), 5 (Bare Except), 6 (Eval/Exec)
    ROLE: Security Compliance. Emits SECURE signal.
    """

    def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Security Audit...")

        keys = [
            (0, self.check_key_00_no_hardcoded_secrets),
            (1, self.check_key_01_no_todo_fixme),
            (2, self.check_key_02_no_print_statements),
            (3, self.check_key_03_no_debugger_statements),
            (4, self.check_key_04_no_empty_except_blocks),
            (5, self.check_key_05_no_bare_except),
            (6, self.check_key_06_no_eval_exec),
        ]

        for key, check_func in keys:
            passed, details = check_func()
            self.ctx.report(self.name, key, passed, details)

        self.ctx.signal_secure()

    def check_key_00_no_hardcoded_secrets(self) -> Tuple[bool, List[str]]:
        violations = []
        patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ]
        
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    content = f.read()
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            violations.append(fp)
                            break
            except:
                continue
        return len(violations) == 0, violations

    def check_key_01_no_todo_fixme(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        if re.search(r'\b(TODO|FIXME)\b', line, re.IGNORECASE):
                            violations.append(f"{fp}:{i}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_02_no_print_statements(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name) and node.func.id == "print":
                            violations.append(f"{fp}:{node.lineno}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_03_no_debugger_statements(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        if re.search(r'\bbreakpoint\(\)|pdb\.set_trace\(\)', line):
                            violations.append(f"{fp}:{i}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_04_no_empty_except_blocks(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler):
                        if not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
                            violations.append(f"{fp}:{node.lineno}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_05_no_bare_except(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler):
                        if node.type is None:
                            violations.append(f"{fp}:{node.lineno}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_06_no_eval_exec(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec"):
                            violations.append(f"{fp}:{node.lineno}")
            except:
                continue
        return len(violations) == 0, violations


class DocumentationAgent(SubAtomicAgent):
    """
    KEYS: 21 (Missing Docstrings)
    ROLE: Pure focus on Docstrings.
    """

    def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Documentation Check...")
        passed, details = self.check_key_21_no_missing_docstrings()
        self.ctx.report(self.name, 21, passed, details)

    def check_key_21_no_missing_docstrings(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        if not ast.get_docstring(node):
                            violations.append(f"{fp}:{node.lineno} {node.name}")
            except:
                continue
        return len(violations) == 0, violations


class NamingAgent(SubAtomicAgent):
    """
    KEYS: 47 (Naming Conventions)
    ROLE: Enforces Snake_Case/PascalCase.
    """

    def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Naming Convention Check...")
        passed, details = self.check_key_47_naming_conventions()
        self.ctx.report(self.name, 47, passed, details)

    def check_key_47_naming_conventions(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                            violations.append(f"{fp}:{node.lineno} function {node.name}")
                    elif isinstance(node, ast.ClassDef):
                        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                            violations.append(f"{fp}:{node.lineno} class {node.name}")
            except:
                continue
        return len(violations) == 0, violations
