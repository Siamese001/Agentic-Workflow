from typing import Any, Optional, Protocol, Dict, List

import ast
import re
from typing import List, Tuple

from agentic_core.canon_base_agent import SubAtomicAgent


class SafetyInspector(SubAtomicAgent):
    """
    KEYS: 0 (Secrets), 1 (TODO/FIXME), 2 (Print), 3 (Debugger), 4 (Empty Except), 5 (Bare Except), 6 (Eval/Exec)
    ROLE: Security Compliance. Emits SECURE signal.
    """

    def execute(self) -> None:
        """
        Executes the security audit by running all defined checks.
        Reports findings to the context and signals security status.
        """
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

    def _check_content_for_secret_patterns(self, content: str, patterns: List[str]) -> bool:
        """Helper to check if file content contains any secret patterns."""
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _read_file_content(self, fp: str) -> Tuple[str, bool]:
        """Helper to read file content, returns content and success status."""
        try:
            with open(fp, "r", encoding="utf-8") as f:
                return f.read(), True
        except Exception:
            # print(f"Error reading file {fp}: {e}")
            return "", False

    def _find_secret_violations_in_file(self, fp: str, patterns: List[str]) -> List[str]:
        """Helper to find hardcoded secrets in a single file."""
        content, success = self._read_file_content(fp)
        if not success:
            return []

        if self._check_content_for_secret_patterns(content, patterns):
            return [fp]
        return []

    def check_key_00_no_hardcoded_secrets(self) -> Tuple[bool, List[str]]:
        """
        Checks for hardcoded secrets (passwords, API keys, tokens) in files.
        """
        violations = []
        patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ]

        for fp in self.ctx.python_files:
            violations.extend(self._find_secret_violations_in_file(fp, patterns))
        return len(violations) == 0, violations

    def _process_file_lines_for_todo_fixme(self, f_obj, fp: str) -> List[str]:
        """Helper to process lines of an open file for TODO/FIXME violations."""
        violations = []
        for i, line in enumerate(f_obj, 1):
            if re.search(r'\b(TODO|FIXME)\b', line, re.IGNORECASE):
                violations.append(f"{fp}:{i}")
        return violations

    def _find_todo_fixme_violations_in_file(self, fp: str) -> List[str]:
        """Helper to find TODO/FIXME comments in a single file."""
        try:
            with open(fp, "r", encoding="utf-8") as f:
                return self._process_file_lines_for_todo_fixme(f, fp)
        except Exception:
            # print(f"Error reading file {fp}: {e}")
            pass
        return []

    def check_key_01_no_todo_fixme(self) -> Tuple[bool, List[str]]:
        """
        Checks for 'TODO' or 'FIXME' comments in files.
        """
        violations = []
        for fp in self.ctx.python_files:
            violations.extend(self._find_todo_fixme_violations_in_file(fp))
        return len(violations) == 0, violations

    def _find_print_violations_in_tree(self, tree: ast.AST, fp: str) -> List[str]:
        """Helper to find print statements in an AST tree."""
        file_violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and \
               isinstance(node.func, ast.Name) and \
               node.func.id == "print":
                file_violations.append(f"{fp}:{node.lineno}")
        return file_violations

    def check_key_02_no_print_statements(self) -> Tuple[bool, List[str]]:
        """
        Checks for 'print()' statements using AST parsing.
        """
        violations = []
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                violations.extend(self._find_print_violations_in_tree(tree, fp))
            except Exception:
                # print(f"Error processing AST for file {fp}: {e}")
                continue
        return len(violations) == 0, violations

    def _find_debugger_violations_in_file(self, fp: str) -> List[str]:
        """Helper to find debugger statements in a single file."""
        file_violations = []
        try:
            with open(fp, "r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if re.search(r'\bbreakpoint\(\)|pdb\.set_trace\(\)', line):
                        file_violations.append(f"{fp}:{i}")
        except Exception:
            # print(f"Error reading file {fp}: {e}")
            pass
        return file_violations

    def check_key_03_no_debugger_statements(self) -> Tuple[bool, List[str]]:
        """
        Checks for debugger statements like 'breakpoint()' or 'pdb.set_trace()'.
        """
        violations = []
        for fp in self.ctx.python_files:
            violations.extend(self._find_debugger_violations_in_file(fp))
        return len(violations) == 0, violations

    def _is_empty_except_block(self, node: ast.ExceptHandler) -> bool:
        """Helper to determine if an ExceptHandler node represents an empty except block."""
        return not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass))

    def _find_empty_except_violations_in_tree(self, tree: ast.AST, fp: str) -> List[str]:
        """Helper to find empty except blocks in an AST tree."""
        file_violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and self._is_empty_except_block(node):
                file_violations.append(f"{fp}:{node.lineno}")
        return file_violations

    def check_key_04_no_empty_except_blocks(self) -> Tuple[bool, List[str]]:
        """
        Checks for empty 'except' blocks or 'except: pass' using AST parsing.
        """
        violations = []
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                violations.extend(self._find_empty_except_violations_in_tree(tree, fp))
            except Exception:
                # print(f"Error processing AST for file {fp}: {e}")
                continue
        return len(violations) == 0, violations

    def _is_bare_except_block(self, node: ast.ExceptHandler) -> bool:
        """Helper to determine if an ExceptHandler node represents a bare except block."""
        return node.type is None

    def _find_bare_except_violations_in_tree(self, tree: ast.AST, fp: str) -> List[str]:
        """Helper to find bare except statements in an AST tree."""
        file_violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and self._is_bare_except_block(node):
                file_violations.append(f"{fp}:{node.lineno}")
        return file_violations

    def check_key_05_no_bare_except(self) -> Tuple[bool, List[str]]:
        """
        Checks for bare 'except:' statements (catching all exceptions) using AST parsing.
        """
        violations = []
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                violations.extend(self._find_bare_except_violations_in_tree(tree, fp))
            except Exception:
                # print(f"Error processing AST for file {fp}: {e}")
                continue
        return len(violations) == 0, violations

    def _is_eval_exec_call(self, node: ast.Call) -> bool:
        """Helper to determine if a Call node represents an eval() or exec() call."""
        return isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec")

    def _find_eval_exec_violations_in_tree(self, tree: ast.AST, fp: str) -> List[str]:
        """Helper to find eval() or exec() calls in an AST tree."""
        file_violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._is_eval_exec_call(node):
                file_violations.append(f"{fp}:{node.lineno}")
        return file_violations

    def check_key_06_no_eval_exec(self) -> Tuple[bool, List[str]]:
        """
        Checks for 'eval()' or 'exec()' function calls using AST parsing.
        """
        violations = []
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                violations.extend(self._find_eval_exec_violations_in_tree(tree, fp))
            except Exception:
                # print(f"Error processing AST for file {fp}: {e}")
                continue
        return len(violations) == 0, violations


class DocumentationAgent(SubAtomicAgent):
    """
    KEYS: 21 (Missing Docstrings)
    ROLE: Pure focus on Docstrings.
    """

    def execute(self) -> None:
        """
        Executes the documentation check, specifically for missing docstrings.
        """
        print(f"\n[>>>] {self.name} ACTIVATED: Documentation Check...")
        passed, details = self.check_key_21_no_missing_docstrings()
        self.ctx.report(self.name, 21, passed, details)

    def _has_missing_docstring(self, node: ast.AST) -> bool:
        """Helper to determine if a node (FunctionDef or ClassDef) has a missing docstring."""
        return not ast.get_docstring(node)

    def _find_missing_docstring_violations_in_tree(self, tree: ast.AST, fp: str) -> List[str]:
        """Helper to find missing docstrings in an AST tree."""
        file_violations = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and self._has_missing_docstring(node):
                file_violations.append(f"{fp}:{node.lineno} {node.name}")
        return file_violations

    def check_key_21_no_missing_docstrings(self) -> Tuple[bool, List[str]]:
        """
        Checks for missing docstrings in classes and functions using AST parsing.
        """
        violations = []
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                violations.extend(self._find_missing_docstring_violations_in_tree(tree, fp))
            except Exception:
                # print(f"Error processing AST for file {fp}: {e}")
                continue
        return len(violations) == 0, violations


class NamingAgent(SubAtomicAgent):
    """
    KEYS: 47 (Naming Conventions)
    ROLE: Enforces Snake_Case/PascalCase.
    """

    def execute(self) -> None:
        """
        Executes the naming convention check.
        """
        print(f"\n[>>>] {self.name} ACTIVATED: Naming Convention Check...")
        passed, details = self.check_key_47_naming_conventions()
        self.ctx.report(self.name, 47, passed, details)

    def _is_invalid_function_name(self, name: str) -> bool:
        """Helper to check if a function name violates PEP 8 snake_case."""
        return not re.match(r'^[a-z_][a-z0-9_]*$', name)

    def _is_invalid_class_name(self, name: str) -> bool:
        """Helper to check if a class name violates PEP 8 PascalCase."""
        return not re.match(r'^[A-Z][a-zA-Z0-9]*$', name)

    def _find_naming_convention_violations_in_tree(self, tree: ast.AST, fp: str) -> List[str]:
        """Helper to find naming convention violations in an AST tree."""
        file_violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and self._is_invalid_function_name(node.name):
                file_violations.append(f"{fp}:{node.lineno} function {node.name}")
            elif isinstance(node, ast.ClassDef) and self._is_invalid_class_name(node.name):
                file_violations.append(f"{fp}:{node.lineno} class {node.name}")
        return file_violations

    def check_key_47_naming_conventions(self) -> Tuple[bool, List[str]]:
        """
        Checks for PEP 8 naming conventions for functions (snake_case)
        and classes (PascalCase) using AST parsing.
        """
        violations = []
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                violations.extend(self._find_naming_convention_violations_in_tree(tree, fp))
            except Exception:
                # print(f"Error processing AST for file {fp}: {e}")
                continue
        return len(violations) == 0, violations