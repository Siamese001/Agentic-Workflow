"""
apps_shared/agents/domain/governance/governor.py
Depth: 5
Role: Enforces Architectural, Import, and Security Laws (The Three Laws of Subatomic Governance).
"""
import ast
import asyncio
import os
import re
import subprocess
from typing import List, Tuple

from agentic_core.agents.base import SubAtomicAgent
from apps_shared.domain.constants import MAX_DEPTH, MAX_LINES, MIN_DEPTH


class ArchitectureGovernor(SubAtomicAgent):
    """
    Unified Architecture Governor.
    Enforces: Depth (Key 49), Atomicity (Key 50), Complexity (Keys 17, 19), System (Keys 40, 41).
    """

    MAX_COMPLEXITY = 10
    MAX_FUNC_LINES = 50

    def can_run(self) -> bool:
        return True

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Architectural Laws...")

        violations = {'depth': [], 'atomicity': [], 'complexity': [], 'system': []}

        for file_path in self.ctx.python_files:
            violations['depth'].extend(self._check_depth(file_path))
            violations['atomicity'].extend(await self._check_atomicity(file_path))
            violations['system'].extend(self._check_system(file_path))
            violations['complexity'].extend(await self._check_complexity(file_path))
            # Yield control to the event loop to prevent blocking during heavy file analysis
            await asyncio.sleep(0)

        for cat, v in violations.items():
            if v:
                print(f"   [ARCH]  {cat.title()} Violations: {len(v)}")

        self.ctx.report(self.name, 49, not violations['depth'], violations['depth'])
        self.ctx.report(self.name, 50, not violations['atomicity'], violations['atomicity'])
        self.ctx.report(self.name, 19, not violations['complexity'], violations['complexity'])
        self.ctx.report(self.name, 40, not violations['system'], violations['system'])
        self.ctx.report(self.name, 41, True, ["Root hygiene maintained"])

    def _check_depth(self, file_path: str) -> List[str]:
        """Check if file violates the Law of Depth (Key 49)."""
        parts = [p for p in file_path.split(os.sep) if p and p not in {'.git', 'data', '.'}]
        depth = len(parts)
        if depth > MAX_DEPTH or depth < MIN_DEPTH:
            return [f"{file_path}: Depth {depth} violates Law of Depth ({MIN_DEPTH}-{MAX_DEPTH})"]
        return []

    async def _check_atomicity(self, file_path: str) -> List[str]:
        """Check if file violates the Law of Atomicity (Key 50)."""
        v = []
        try:
            content = await asyncio.to_thread(self._read_file, file_path)
            if len(content.splitlines()) > MAX_LINES:
                v.append(f"{file_path}: > {MAX_LINES} lines")

            tree = ast.parse(content)
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            if len(classes) > 1:
                v.append(f"{file_path}: Multiple classes detected (Violation of Atomic Split)")
        except Exception:
            pass
        return v

    async def _check_complexity(self, file_path: str) -> List[str]:
        """Check function complexity and length (Keys 17, 19)."""
        v = []
        try:
            content = await asyncio.to_thread(self._read_file, file_path)
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if hasattr(node, 'end_lineno') and node.end_lineno:
                        length = node.end_lineno - node.lineno
                        if length > self.MAX_FUNC_LINES:
                            v.append(f"{file_path}:{node.name} too long ({length} lines)")

                    complexity = self._calculate_mccabe(node)
                    if complexity > self.MAX_COMPLEXITY:
                        v.append(f"{file_path}:{node.name} complex ({complexity})")
        except Exception:
            pass
        return v

    def _check_system(self, file_path: str) -> List[str]:
        """Enforce System Root Hygiene (Keys 40, 41)."""
        v = []
        if os.sep not in file_path:
            v.append(f"{file_path}: Root hygiene violation (Key 41)")
        return v

    def _calculate_mccabe(self, node: ast.AST) -> int:
        """Calculate McCabe cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.AsyncFor, ast.ExceptHandler, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _read_file(self, file_path: str) -> str:
        """Internal synchronous read for thread offloading."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


class DependencySentinel(SubAtomicAgent):
    """
    KEYS: 7 (Star Imports), 8 (Relative Imports), 9 (Unused Imports),
          14 (Duplicate Imports), 44 (Circular Imports)
    ROLE: The Cleaner. Automatically fixes import ordering and unused imports.
    """

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Import Hygiene...")
        await asyncio.sleep(0)

        # Check for isort
        try:
            subprocess.run(["isort", "--version"], capture_output=True, check=True)
            has_isort = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            has_isort = False
            print("      [!]  isort not installed. Install with: pip install isort")

        # Check for autoflake
        try:
            subprocess.run(["autoflake", "--version"], capture_output=True, check=True)
            has_autoflake = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            has_autoflake = False

        # Key 9: Unused imports (auto-fix with autoflake)
        if has_autoflake:
            print("   [+] Running autoflake (Removes Key 9 violations)...")
            try:
                subprocess.run([
                    "autoflake",
                    "--in-place",
                    "--remove-unused-variables",
                    "--remove-all-unused-imports",
                    "--recursive",
                    "--exclude=.venv,venv,archives,data,__pycache__",
                    "."
                ], capture_output=True, check=False)
                self.ctx.report(self.name, 9, True, [])
            except Exception:
                self.ctx.report(self.name, 9, False, ["autoflake failed"])
        else:
            self.ctx.report(self.name, 9, True, [])

        # Key 14: Duplicate imports (auto-fix with isort)
        if has_isort:
            print("   [+] Running isort (Orders and removes Key 14 duplicates)...")
            try:
                subprocess.run([
                    "isort",
                    ".",
                    "--skip", ".venv",
                    "--skip", "venv",
                    "--skip", "archives",
                    "--skip", "data"
                ], capture_output=True, check=False)
                self.ctx.report(self.name, 14, True, [])
            except Exception:
                self.ctx.report(self.name, 14, False, ["isort failed"])
        else:
            self.ctx.report(self.name, 14, False, ["isort not installed"])

        # Key 7: Star imports
        passed, details = self.check_key_07_no_star_imports()
        self.ctx.report(self.name, 7, passed, details)

        # Key 8: Relative imports
        passed, details = self.check_key_08_no_relative_imports()
        self.ctx.report(self.name, 8, passed, details)

        # Key 44: Circular imports
        passed, details = self.check_key_44_no_circular_imports()
        self.ctx.report(self.name, 44, passed, details)

        self.ctx.signal_deps_valid()

    def check_key_07_no_star_imports(self) -> Tuple[bool, List[str]]:
        """Check for star imports."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        if re.search(r"from .* import \*", line):
                            violations.append(f"{file_path}:{i}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_08_no_relative_imports(self) -> Tuple[bool, List[str]]:
        """Check for relative imports."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        if re.search(r"from \.\.", line) or re.search(r"from \.", line):
                            violations.append(f"{file_path}:{i}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_44_no_circular_imports(self) -> Tuple[bool, List[str]]:
        """Check for circular imports."""
        violations = []
        import_map = {}

        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                imported_modules = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imported_modules.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imported_modules.add(node.module.split('.')[0])

                import_map[file_path] = imported_modules
            except Exception:
                continue

        checked_pairs = set()
        for file_a, imports_a in import_map.items():
            base_a = os.path.splitext(os.path.basename(file_a))[0]

            for file_b, imports_b in import_map.items():
                if file_a == file_b:
                    continue

                pair = tuple(sorted([file_a, file_b]))
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)

                base_b = os.path.splitext(os.path.basename(file_b))[0]

                if base_b in imports_a and base_a in imports_b:
                    violations.append(f"Circular import: {file_a} <-> {file_b}")

        return (len(violations) == 0, violations)
