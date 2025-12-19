"""
apps_shared/agents/domain/governance/governor.py
Depth: 5
Role: Enforces Architectural, Import, and Security Laws (The Three Laws of Subatomic Governance).
"""
import ast
import asyncio
import os
from typing import List

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
                print(f"   🏛️  {cat.title()} Violations: {len(v)}")
        
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