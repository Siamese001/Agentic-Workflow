from __future__ import annotations
import ast
'''Brief description of functionality and purpose.'''

import hashlib
import json
import re
from typing import Any, Dict, List, Optional, Protocol, Tuple

from agentic_core.L0_maintenance.scripts.canon_validator_config import MAX_LINES
from agentic_core.L2_execution.ToolRegistry.base import SubAtomicAgent

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin


# NAMING CANON ETERNAL — renamed inline for sovereign discovery — Phase 5 — 2025-12-30
class StructuralEngineerAgent(SubAtomicAgent):
    """
    KEYS: 18 (Many Parameters), 20 (Large Classes), 25 (Globals), 42 (Large Files), 43 (Class Density), 46 (Duplicate Code)
    ROLE: Heavy Refactoring with Semantic Intelligence.
    """

    def can_run(self) -> bool:
                    
        return "GENERATIVE_CLEAN" in self.ctx.signals

    async def execute(self) -> None:
        """Execute Structural Engineer validation checks."""
        print(f"\nfrom agentic_core.L2_execution.ToolRegistry.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.utils.core_extensions.healer_mixin import HealerMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n[>>>] {self.name} ACTIVATED: Checking Code Structure...")
        print(f"   [{self.name}] 🔧 Analyzing structural integrity...")

        # Key 17: Large functions
        print(f"   [{self.name}] 🔍 Checking Key 17: Large Functions...")
        passed, details = self.check_key_17_no_large_functions()
        if passed:
            print(f"   [{self.name}] ✅ Key 17: PASS - All functions within limits")
        else:
            print(f"   [{self.name}] ❌ Key 17: FAIL ({len(details)} violations)")
        self.ctx.report(self.name, 17, passed, details)

        # Key 18: Many parameters
        print(f"   [{self.name}] 🔍 Checking Key 18: Parameter Count...")
        passed, details = self.check_key_18_no_many_parameters()
        if passed:
            print(f"   [{self.name}] ✅ Key 18: PASS - Parameter counts acceptable")
        else:
            print(f"   [{self.name}] ❌ Key 18: FAIL ({len(details)} violations)")
        self.ctx.report(self.name, 18, passed, details)

        # Key 19: Complexity (already checked above)
        # Key 20: Large classes (>200 lines)
        print(f"   [{self.name}] 🔍 Checking Key 20: Large Classes...")
        passed, details = self.check_key_20_no_large_classes()
        if passed:
            print(f"   [{self.name}] ✅ Key 20: PASS - All classes within limits")
        else:
            print(f"   [{self.name}] ❌ Key 20: FAIL ({len(details)} violations)")
        self.ctx.report(self.name, 20, passed, details)

        # Key 25: Global variables
        print(f"   [{self.name}] 🔍 Checking Key 25: Global Variables...")
        passed, details = self.check_key_25_no_global_variables()
        if passed:
            print(f"   [{self.name}] ✅ Key 25: PASS - No global variables detected")
        else:
            print(f"   [{self.name}] ❌ Key 25: FAIL ({len(details)} violations)")
        self.ctx.report(self.name, 25, passed, details)

        # Key 42: Large files (>500 lines)
        print(f"   [{self.name}] 🔍 Checking Key 42: Large Files...")
        passed, details = self.check_key_42_no_large_files()
        if passed:
            print(f"   [{self.name}] ✅ Key 42: PASS - All files within size limits")
        else:
            print(f"   [{self.name}] ❌ Key 42: FAIL ({len(details)} violations)")
        self.ctx.report(self.name, 42, passed, details)

        # Key 43: Class density (>10 classes per file)
        print(f"   [{self.name}] 🔍 Checking Key 43: Class Density...")
        passed, details = self.check_key_43_no_class_density()
        if passed:
            print(f"   [{self.name}] ✅ Key 43: PASS - Class density acceptable")
        else:
            print(f"   [{self.name}] ❌ Key 43: FAIL ({len(details)} violations)")
        self.ctx.report(self.name, 43, passed, details)

        # Key 46: Duplicate code
        print(f"   [{self.name}] 🔍 Checking Key 46: Duplicate Code...")
        passed, details = self.check_key_46_no_duplicate_code()
        if passed:
            print(f"   [{self.name}] ✅ Key 46: PASS - No duplicate code detected")
        else:
            print(f"   [{self.name}] ❌ Key 46: FAIL ({len(details)} violations)")
        self.ctx.report(self.name, 46, passed, details)

        print(f"   [{self.name}] ✅ Structural analysis complete")
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

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


# NAMING CANON ETERNAL — renamed inline for sovereign discovery — Phase 5 — 2025-12-30
class PatternEnforcerAgent(HealerMixin, SubatomicTestingMixin, SubAtomicAgent, MCPHardenedMixin):
    """
    KEYS: 26-39 (Pattern Checks)
    ROLE: Enforces coding patterns and best practices.
    """

    async def execute(self) -> None:
                    
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
    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
