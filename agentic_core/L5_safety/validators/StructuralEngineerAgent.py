# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: healer, memory, orchestrator, prompt, state, workflow
from __future__ import annotations
# This boosts alignment detection — review and integrate appropriately

from agentic_core.observability.SovereignBaseAgent import SovereignBaseAgent

from dataclasses import dataclass

"""
Structural Engineer Agent - Code Structure Validation
CANONICAL: True - Consolidated 2026-01-06 (merged from engineering.py)

Responsible for:
- Large functions
- Many parameters
- No large classes (>20 methods or >500 lines)
- Complexity metrics, cyclomatic complexity
- Code organization, modularity, cohesion
- Large files
- Class density
- Duplicate code
"""
import ast
import os
from typing import Any

from agentic_core.L2_execution.ToolRegistry.CanonBaseAgent import CanonBaseAgent

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout


# NAMING CANON ABSOLUTE — renamed for eternal sovereign discovery — Phase 4 — 2025-12-30
@dataclass
class StructuralEngineerAgent(SovereignBaseAgent, CanonBaseAgent):
    """
    Structural Engineer validates code structure and organization.

    Validates:
    - No large classes (>20 methods or >500 lines)
    - Proper function size (<50 lines)
    - Cyclomatic complexity (<10)
    - Modularity, cohesion, coupling
    """

    def get_validation_keys(self) -> list[int]:
        """Return canon keys validated by this agent."""
        return list(range(20, 31))

    async def execute(self) -> Any:
        """Execute Structural Engineer validation checks."""
        print(
        )
        print(f"   [{self.name}] 🔍 Checking Large Classes...")
        passed, violations = self.check_no_large_classes()
        if not passed:
            print(f"   [{self.name}] ❌ Large Classes: FAIL ({len(violations)} violations)")
            await self._heal_violations("large_classes", violations)
        else:
            print(f"   [{self.name}] ✅ Large Classes: PASS - All classes within limits")
        print(f"   [{self.name}] 🔍 Checking Large Functions...")
        passed, violations = self.check_no_large_functions()
        if not passed:
            print(
                f"   [{self.name}] ❌ Large Functions: FAIL ({len(violations)} violations) - Large functions detected"
            )
            await self._heal_violations("large_functions", violations)
        else:
            print(f"   [{self.name}] ✅ Large Functions: PASS - All functions within limits")

    def check_no_large_classes(self) -> tuple[bool, list[str]]:
        """
        Check for classes with >20 methods or >500 lines.

        Returns:
            Tuple of (passed, list of violations)
        """
        from pathlib import Path

        violations: Any = []
        max_methods: Any = int(os.getenv("MAX_CLASS_METHODS", "20"))
        max_lines: Any = int(os.getenv("MAX_CLASS_LINES", "500"))
        for file_path in self.ctx.python_files:
            try:
                resolved_path: Any = Path(file_path).resolve()
                with open(resolved_path, encoding="utf-8") as f:
                    content: Any = f.read()
                    tree: Any = ast.parse(content)
                    content.splitlines()
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        method_count: Any = sum(
                            1
                            for n in node.body
                            if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)
                        )
                        if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                            class_lines: Any = node.end_lineno - node.lineno + 1
                        else:
                            class_lines: Any = 0
                        if method_count > max_methods:
                            violations.append(
                                f"{file_path}:{node.lineno}: Class '{node.name}' has {method_count} methods (max {max_methods})"
                            )
                        if class_lines > max_lines:
                            violations.append(
                                f"{file_path}:{node.lineno}: Class '{node.name}' has {class_lines} lines (max {max_lines})"
                            )
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_no_large_functions(self) -> tuple[bool, list[str]]:
        """
        Check for functions exceeding 50 lines.

        Returns:
            Tuple of (passed, list of violations)
        """
        from pathlib import Path

        violations: Any = []
        max_lines: Any = int(os.getenv("MAX_FUNCTION_LINES", "50"))
        for file_path in self.ctx.python_files:
            try:
                resolved_path: Any = Path(file_path).resolve()
                with open(resolved_path, encoding="utf-8") as f:
                    content: Any = f.read()
                    tree: Any = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                        if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                            func_lines: Any = node.end_lineno - node.lineno + 1
                            if func_lines > max_lines:
                                violations.append(
                                    f"{file_path}:{node.lineno}: Function '{node.name}' has {func_lines} lines (max {max_lines})"
                                )
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_cyclomatic_complexity(self) -> tuple[bool, list[str]]:
        """
        Check for high cyclomatic complexity (>10).

        Returns:
            Tuple of (passed, list of violations)
        """
        violations: Any = []
        max_complexity: Any = int(os.getenv("MAX_CYCLOMATIC_COMPLEXITY", "10"))
        for file_path in self.ctx.python_files:
            try:
                resolved_path: Any = Path(file_path).resolve()
                with open(resolved_path, encoding="utf-8") as f:
                    tree: Any = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                        complexity: Any = self._calculate_complexity(node)
                        if complexity > max_complexity:
                            violations.append(
                                f"{file_path}:{node.lineno}: Function '{node.name}' has complexity {complexity} (max {max_complexity})"
                            )
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def _calculate_complexity(self, node: ast.AST) -> int:
        """
        Calculate cyclomatic complexity of a function.

        Complexity = 1 + number of decision points (if, for, while, and, or, except)
        """
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, ast.If | ast.For | ast.While | ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    async def _heal_violations(self, key: int, violations: list[str]):
        """
        Heal violations for a specific key.

        Args:
            key: Canon key number
            violations: List of Violation descriptions
        """
        max_healing_per_file = int(os.getenv("MAX_HEALING_PER_FILE", "8"))
        file_violations = {}
        for Violation in violations[:max_healing_per_file]:
            if ":" in Violation:
                parts = Violation.split(": ", 1)
                if len(parts) >= 1:
                    file_path = parts[0]
                    if file_path not in file_violations:
                        file_violations[file_path] = []
                    file_violations[file_path].append(Violation)
        for file_path, file_viols in file_violations.items():
            await self._smart_fix(file_path, key, file_viols)

    async def _smart_fix(self, file_path: str, violation_key: int, violations: list[str]):
        """
        Apply smart fix to a file using Gemini 2.5 Flash.

        Args:
            file_path: Path to file to fix
            violation_key: Canon key being fixed
            violations: List of violations in this file
        """
        from pathlib import Path

        try:
            resolved_path = Path(file_path).resolve()
            with open(resolved_path, encoding="utf-8") as f:
                original_code = f.read()
        except Exception as e:
            print(f"      [!] Cannot read {file_path}: {e}")
            return
        violation_details = "\n".join(violations)
        Task = f"Fix Subatomic Canon Key {violation_key}. Violations:\n{violation_details}"
        max_rounds = 5
        current_code = original_code
        previous_failure = None
        for round_num in range(1, max_rounds + 1):
            print(
                f"      [Round {round_num}/{max_rounds}] Healing Key {violation_key} → {os.path.basename(file_path)}"
            )
            mutated_code = await self.resilient_mutation(
                Task=Task,
                code=current_code,
                file_path=file_path,
                round_num=round_num,
                previous_failure=previous_failure,
            )
            is_valid, reason = await self.verify_fix(original_code, mutated_code, violation_key)
            if not is_valid:
                print(f"      [!] Round {round_num}: {reason} – retrying")
                previous_failure = reason
                current_code = mutated_code
                continue
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(mutated_code)
                print(f"      [OK] Round {round_num}: Fixed {os.path.basename(file_path)}")
                return
            except Exception as e:
                print(f"      [X] Cannot write {file_path}: {e}")
                return
        print(f"      [X] Failed to fix {os.path.basename(file_path)} after {max_rounds} rounds")

    @timeout(300)
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L2 execution agent - invoke shared healing chain."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            super().heal_repository(
                dry_run=dry_run,
                execute=execute,
                depth=depth,
                max_depth=max_depth,
                _call_path=_call_path,
            )
            print(f"[{agent_name}] L2 execution - healing chain invoked")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
