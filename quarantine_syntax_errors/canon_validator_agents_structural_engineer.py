"""
StructuralEngineer Agent - Heavy Refactoring with Semantic Intelligence.
KEYS: 17 (Large Functions), 18 (Many Parameters), 20 (Large Classes),
      25 (Globals), 42 (Large Files), 43 (Class Density), 46 (Duplicate Code)
"""

import ast
import asyncio
import hashlib
from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    pass

from agentic_core..base import SubAtomicAgent
from agentic_core..config import MAX_LINES


class StructuralEngineer(SubAtomicAgent):
    """
    KEYS: 17, 18, 20, 25, 42, 43, 46
    ROLE: Heavy Refactoring with Semantic Intelligence.
    """

    def can_run(self) -> bool:
        return "GENERATIVE_CLEAN" in self.ctx.signals

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Reviewing Structural Integrity...")
        await asyncio.sleep(0)

        self.ctx.report(self.name, 17, *self.check_key_17_no_large_functions())
        self.ctx.report(self.name, 18, *self.check_key_18_no_many_parameters())
        self.ctx.report(self.name, 20, *self.check_key_20_no_large_classes())
        self.ctx.report(self.name, 25, *self.check_key_25_no_global_variables())
        self.ctx.report(self.name, 42, *self.check_key_42_no_large_files())
        self.ctx.report(self.name, 43, *self.check_key_43_no_class_density())
        self.ctx.report(self.name, 46, *self.check_key_46_no_duplicate_code())

        print("   ✅ Structural analysis complete.")

    def check_key_17_no_large_functions(self) -> Tuple[bool, List[str]]:
        """Check for large functions (>50 lines)."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if hasattr(node, 'end_lineno'):
                            func_lines = node.end_lineno - node.lineno + 1
                            if func_lines > 50:
                                violations.append(f"{file_path}:{node.lineno} ({func_lines} lines)")
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
                        total_params = len(node.args.args) + len(node.args.kwonlyargs)
                        if node.args.vararg:
                            total_params += 1
                        if node.args.kwarg:
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
                        if hasattr(node, 'end_lineno'):
                            class_lines = node.end_lineno - node.lineno + 1
                            if class_lines > 200:
                                violations.append(f"{file_path}:{node.lineno} {node.name} ({class_lines} lines)")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_25_no_global_variables(self) -> Tuple[bool, List[str]]:
        """Check for global variables (non-constant)."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in tree.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                if not target.id.isupper():
                                    violations.append(f"{file_path}:{node.lineno}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_42_no_large_files(self) -> Tuple[bool, List[str]]:
        """Check for large files (>MAX_LINES)."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if len(lines) > MAX_LINES:
                        violations.append(f"{file_path} ({len(lines)} lines)")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_43_no_class_density(self) -> Tuple[bool, List[str]]:
        """Check for too many classes in one file (>10)."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
                if class_count > 10:
                    violations.append(f"{file_path} ({class_count} classes)")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_46_no_duplicate_code(self) -> Tuple[bool, List[str]]:
        """Check for duplicate code (identical files)."""
        violations = []
        file_hashes = {}
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "rb") as f:
                    content_hash = hashlib.md5(f.read()).hexdigest()
                if content_hash in file_hashes:
                    violations.append(f"Duplicate: {file_path} (same as {file_hashes[content_hash]})")
                else:
                    file_hashes[content_hash] = file_path
            except Exception:
                continue
        return (len(violations) == 0, violations)
