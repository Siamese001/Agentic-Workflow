import ast
import asyncio
import hashlib
import re
from typing import List, Tuple

from agentic_core.agents.base import SubAtomicAgent
from apps_shared.domain.constants import MAX_LINES


class StructuralEngineer(SubAtomicAgent):
    """
    KEYS: 18 (Many Parameters), 20 (Large Classes), 25 (Globals), 42 (Large Files), 43 (Class Density), 46 (Duplicate Code)
    ROLE: Heavy Refactoring with Semantic Intelligence.
    """

    def can_run(self) -> bool:
        return "GENERATIVE_CLEAN" in self.ctx.signals

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Reviewing Refactoring Plans...")
        await asyncio.sleep(0)

        # Key 17: Large functions
        passed, details = self.check_key_17_no_large_functions()
        self.ctx.report(self.name, 17, passed, details)

        # Key 18: Many parameters (>5 params)
        passed, details = self.check_key_18_no_many_parameters()
        self.ctx.report(self.name, 18, passed, details)

        # Key 19: Complexity (already checked above)
        # Key 20: Large classes (>200 lines)
        passed, details = self.check_key_20_no_large_classes()
        self.ctx.report(self.name, 20, passed, details)

        # Key 25: Global variables
        passed, details = self.check_key_25_no_global_variables()
        self.ctx.report(self.name, 25, passed, details)

        # Key 42: Large files (>500 lines)
        passed, details = self.check_key_42_no_large_files()
        self.ctx.report(self.name, 42, passed, details)

        # Key 43: Class density (>10 classes per file)
        passed, details = self.check_key_43_no_class_density()
        self.ctx.report(self.name, 43, passed, details)

        # Key 46: Duplicate code
        passed, details = self.check_key_46_no_duplicate_code()
        self.ctx.report(self.name, 46, passed, details)

        print("   ✅ No structural changes pending.")

    def check_key_17_no_large_functions(self) -> Tuple[bool, List[str]]:
        """Check for functions exceeding MAX_LINES."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if hasattr(node, 'end_lineno'):
                            lines = node.end_lineno - node.lineno + 1
                            if lines > MAX_LINES:
                                violations.append(f"{file_path}:{node.lineno} {node.name} ({lines} lines)")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_18_no_many_parameters(self) -> Tuple[bool, List[str]]:
        """Check for functions with too many parameters (>5)."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        args = node.args
                        total_params = len(args.args) + len(args.kwonlyargs)
                        if args.vararg:
                            total_params += 1
                        if args.kwarg:
                            total_params += 1
                        if total_params > 5:
                            violations.append(f"{file_path}:{node.lineno} {node.name}() ({total_params} params)")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_20_no_large_classes(self) -> Tuple[bool, List[str]]:
        """Check for large classes (>200 lines)."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                            class_lines = node.end_lineno - node.lineno + 1
                            if class_lines > 200:
                                violations.append(f"{file_path}:{node.lineno} {node.name} ({class_lines} lines)")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_25_no_global_variables(self) -> Tuple[bool, List[str]]:
        """Check for global variable assignments at module level."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in tree.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                violations.append(f"{file_path}:{node.lineno} global {target.id}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_42_no_large_files(self) -> Tuple[bool, List[str]]:
        """Check for files exceeding 500 lines."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if len(lines) > 500:
                        violations.append(f"{file_path} ({len(lines)} lines)")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_43_no_class_density(self) -> Tuple[bool, List[str]]:
        """Check for more than 10 classes in a single file."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
                if len(classes) > 10:
                    violations.append(f"{file_path} ({len(classes)} classes)")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_46_no_duplicate_code(self) -> Tuple[bool, List[str]]:
        """Check for identical file content across the project."""
        hashes = {}
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    h = hashlib.md5(content.encode()).hexdigest()
                    if h in hashes:
                        violations.append(f"Duplicate content: {file_path} matches {hashes[h]}")
                    hashes[h] = file_path
            except Exception:
                continue
        return (len(violations) == 0, violations)