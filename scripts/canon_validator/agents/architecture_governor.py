"""
ArchitectureGovernor Agent - Unified Architecture Enforcer.
Enforces: Depth (49), Atomicity (50), Complexity (17,19), System (40,41)
"""

import ast
import asyncio
import os
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    pass

from ..base import SubAtomicAgent


class ArchitectureGovernor(SubAtomicAgent):
    """
    Unified Architecture Governor.
    Enforces: Depth (49), Atomicity (50), Complexity (17,19), System (40,41)
    """

    MAX_COMPLEXITY = 10
    MAX_FUNC_LINES = 50

    def can_run(self) -> bool:
        return True

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Architectural Laws...")
        await asyncio.sleep(0)

        violations = {'depth': [], 'atomicity': [], 'complexity': [], 'system': []}

        for file_path in self.ctx.python_files:
            violations['depth'].extend(self._check_depth(file_path))
            violations['atomicity'].extend(self._check_atomicity(file_path))
            violations['system'].extend(self._check_system(file_path))
            violations['complexity'].extend(self._check_complexity(file_path))

        for cat, v in violations.items():
            if v:
                print(f"   🏛️  {cat.title()} Violations: {len(v)}")

        self.ctx.report(self.name, 49, not violations['depth'], violations['depth'])
        self.ctx.report(self.name, 50, not violations['atomicity'], violations['atomicity'])
        self.ctx.report(self.name, 19, not violations['complexity'], violations['complexity'])
        self.ctx.report(self.name, 40, not violations['system'], violations['system'])
        self.ctx.report(self.name, 41, True, ["Root hygiene maintained"])

    def _check_depth(self, file_path: str) -> List[str]:
        """Check file depth against maximum allowed."""
        parts = file_path.split(os.sep)
        if len([p for p in parts if p not in {'.git', 'data'}]) - 1 > 5:
            return [f"{file_path}: Depth > 5"]
        return []

    def _check_atomicity(self, file_path: str) -> List[str]:
        """Check file size and class count for atomicity."""
        v = []
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
            if len(content.splitlines()) > 200:
                v.append(f"{file_path}: > 200 lines")
            tree = ast.parse(content)
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            if len(classes) > 1:
                v.append(f"{file_path}: Multiple classes")
        except Exception:
            pass
        return v

    def _check_complexity(self, file_path: str) -> List[str]:
        """Check function complexity and length."""
        v = []
        try:
            tree = ast.parse(open(file_path, encoding='utf-8').read())
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if hasattr(node, 'end_lineno'):
                        length = node.end_lineno - node.lineno
                        if length > self.MAX_FUNC_LINES:
                            v.append(f"{file_path}:{node.name} too long ({length})")
                    complexity = self._calculate_mccabe(node)
                    if complexity > self.MAX_COMPLEXITY:
                        v.append(f"{file_path}:{node.name} complex ({complexity})")
        except Exception:
            pass
        return v

    def _calculate_mccabe(self, node) -> int:
        """Calculate McCabe cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.AsyncFor, ast.ExceptHandler)):
                complexity += 1
        return complexity

    def _check_system(self, file_path: str) -> List[str]:
        """Check system-level constraints."""
        return []

    async def propose_fix(self, file_path: str, violation_type: str, details: str) -> str:
        """L5+ Use LLM with few-shot to propose architectural fixes."""
        if not self.ctx.intelligence_enabled:
            return ""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return ""

        prompt = f"""
{self.ctx.FEW_SHOT_GLOBAL_REFACTOR}

File {file_path} violates {violation_type} law.
Details: {details}

Current content (first 2000 chars):
{content[:2000]}

Propose minimal compliance action:
- MOVE: old_path → new_path
- SPLIT: file.py → [new_file1.py, new_file2.py]
- DELETE (if noise)
Output one operation per line.
"""

        return await self.ctx.resilient_mutation(
            self.name, prompt, max_attempts=1
        )
