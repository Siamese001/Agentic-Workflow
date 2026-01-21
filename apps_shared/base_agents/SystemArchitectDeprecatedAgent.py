
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, validator, workflow
# This boosts alignment detection — review and integrate appropriately

from dataclasses import dataclass

"""
SystemArchitectDeprecatedAgent - Extracted from CanonHealerAgent.py
Legacy system architect logic preserved for backward compatibility.
Renamed from _SystemArchitect_Deprecated to comply with strict discovery rules.
"""
from __future__ import annotations

import ast
import logging
import os
import sys
from pathlib import Path
from typing import Any

from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from apps_shared.base_agents.canon_base_agent_interface import CanonBaseAgentInterface

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin


# Legacy class removed - use SystemArchitectAgent instead
@dataclass
class SystemArchitectDeprecatedAgent(SubatomicTestingMixin, HealerMixin, CanonBaseAgentInterface, MCPHardenedMixin):
    """
    KEYS: 40 (Metaclasses), 41 (Deep Nesting), 49 (Directory Depth), 50 (Integrity)
    ROLE: The Gatekeeper. If this fails, the system is unstable.
    Phase 9A: DDD Remediation - Composition over inheritance
    """

    def __init__(self, ctx: Any = None) -> None:
        """Initialize the instance."""
        self.impl = None  # CanonBaseAgent is abstract, skip instantiation
        self.ctx = ctx
        self.name = self.__class__.__name__
        self.Logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def execute(self, goal: str = None, context: dict[str, Any] = None) -> dict[str, Any]:
        """Execute validation checks - maintains backward compatibility."""
        await self._execute_validation()
        return {"status": "completed", "agent": self.name}

    def get_capabilities(self) -> list[str]:
        """Execute get_capabilities operation."""
        return self.impl.get_capabilities()

    def validate_state(self) -> bool:
        """Execute validate_state operation."""
        return self.impl.validate_state()

    async def _execute_validation(self) -> Any:
        """
        Executes the SystemArchitect's checks for core architectural integrity.
        Reports on metaclass usage, nesting depth, directory depth, and root-level file content.
        """
        print(f"\n[>>>] {self.name} ACTIVATED: Verifying Core Architecture...")

        # Key 40: No Metaclasses
        passed_40, details_40 = self.check_key_40_no_metaclasses()
        self.ctx.report(self.name, 40, passed_40, details_40)
        # Key 41: Scoped Nesting
        passed_41, details_41 = self.check_key_41_scoped_nesting()
        if not passed_41 and self.ctx.intelligence_enabled:
            await self._handle_key_41_fix_attempts(details_41)
            # Re-check after attempted fixes
            passed_41, details_41 = self.check_key_41_scoped_nesting()
        self.ctx.report(self.name, 41, passed_41, details_41)

        # Key 49: Directory Depth
        passed_49, details_49 = self.check_key_49_directory_depth()
        self.ctx.report(self.name, 49, passed_49, details_49)
        if not passed_49:
            # Signal critical failure after reporting
            self.ctx.signal_critical_failure()

        # Key 50: Law of Void
        passed_50, details_50 = self.check_key_50_law_of_void()
        self.ctx.report(self.name, 50, passed_50, details_50)

    def _parse_python_file(self, file_path: str) -> ast.AST | None:
        """Helper to safely parse a Python file into an AST."""
        try:
            with open(file_path, encoding="utf-8") as f:
                return ast.parse(f.read(), filename=file_path)
        except (FileNotFoundError, SyntaxError, UnicodeDecodeError) as e:
            print(
                f"Warning: Could not parse {file_path} for check: {e}",
                file=sys.stderr
            )
            return None

    def _has_metaclass_keyword(self, node: ast.ClassDef) -> bool:
        """Helper to check if a ClassDef node has a metaclass keyword."""
        return any(kw.arg == "metaclass" for kw in node.keywords)

    def _check_tree_for_metaclasses(self, tree: ast.AST, file_path: str) -> list[str]:
        """
        Helper method to check an AST tree for metaclass definitions.
        Reduces nesting depth in the main check_key_40_no_metaclasses method.
        """
        violations_in_tree = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if self._has_metaclass_keyword(node):
                    violations_in_tree.append(f"{file_path}:{node.lineno}")
        return violations_in_tree

    def check_key_40_no_metaclasses(self) -> tuple[bool, list[str]]:
        """
        Checks for metaclass usage in Python files.

        Returns:
            A tuple containing:
            - bool: True if no metaclass violations are found, False otherwise.
            - List[str]: A list of strings, each indicating a file path and line number
                          where a metaclass was found.
        """
        metaclass_violations = []
        for file_path in self.ctx.python_files:
            tree = self._parse_python_file(file_path)
            if tree:
                metaclass_violations.extend(self._check_tree_for_metaclasses(tree, file_path))

        return len(metaclass_violations) == 0, metaclass_violations

    def check_key_41_scoped_nesting(self) -> tuple[bool, list[str]]:
        """
        Checks for excessive nesting depth within functions and classes,
        considering a maximum depth from environment variable.
        Returns:
            A tuple containing:
            - bool: True if no nesting depth violations are found, False otherwise.
            - List[str]: A list of strings, each indicating a file path, line number,
                          scope, and depth where a Violation occurred.
        """
        MAX_NESTING_DEPTH = int(os.getenv('MAX_NESTING_DEPTH', '4'))
        violations = []

        for fp in self.ctx.python_files:
            tree = self._parse_python_file(fp)
            if tree:
                # Instantiate the module-level NestVisitor
                visitor = NestVisitor(fp, MAX_NESTING_DEPTH)
                visitor.visit(tree)
                violations.extend(visitor.violations_in_file)
        return len(violations) == 0, violations

    def check_key_49_directory_depth(self) -> tuple[bool, list[str]]:
        """
        Checks the directory depth of Python files within the project.
        Enforces 3 ≤ depth ≤ 5. Files shallower than 3 or deeper than 5
        are considered violations.

        Assumes `self.ctx.python_files` provides paths relative to the project root
        or that `Path(file_path).parts` provides the intended logical depth.

        Returns:
            A tuple containing:
            - bool: True if no critical directory depth violations are found, False otherwise.
            - List[str]: A list of strings, each indicating a file path and its depth
                          for both violations and warnings.
        """
        violations = []
        for file_path in self.ctx.python_files:
            # Path.parts includes all components
            parts = Path(file_path).parts
            depth = len(parts)

            # Skip __init__.py files
            if file_path.endswith("__init__.py"):
                continue

            # [SSOT] Check against per-root required depth from SOVEREIGN_REGISTRY
            if parts and parts[0] in DEPTH_MAP:
                root_folder = parts[0]
                required_depth = DEPTH_MAP[root_folder]
                if depth != required_depth:
                    violations.append(f"{file_path} (Invalid depth: {depth} - {root_folder} requires depth {required_depth})")
        return len(violations) == 0, violations

    def _has_definitions_in_tree(self, ast_tree: ast.AST) -> bool:
        """Helper to check if an AST tree contains class or function definitions."""
        for node in ast_tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                return True
        return False

    def _check_file_for_definitions(self, file_path: str) -> bool:
        """Helper to check if a file contains class or function definitions."""
        tree = self._parse_python_file(file_path)
        if tree:
            return self._has_definitions_in_tree(tree)
        # Treat unparseable as a Violation for safety if parsing failed
        return True

    def _is_root_file_with_definitions(self, file_path: str) -> bool:
        """Helper to check if a file is at root depth and contains definitions."""
        if len(Path(file_path).parts) == 1:
            if self._check_file_for_definitions(file_path):
                return True
        return False

    def check_key_50_law_of_void(self) -> tuple[bool, list[str]]:
        """
        Checks for Python files directly in the project root (depth 1) that contain
        class or function definitions. Such files should ideally be minimal or
        serve as entry points without complex logic, adhering to the "Law of Void".

        Assumes `self.ctx.python_files` provides paths relative to the project root.

        Returns:
            A tuple containing:
            - bool: True if no root-level files contain class/function definitions, False otherwise.
            - List[str]: A list of file paths that violate the "Law of Void".
        """
        root_violations = []
        for file_path in self.ctx.python_files:
            if self._is_root_file_with_definitions(file_path):
                root_violations.append(file_path)
        return len(root_violations) == 0, root_violations

    async def _handle_key_41_fix_attempts(self, details_41: list[str]) -> Any:
        """Helper to attempt smart fixes for Key 41 violations."""
        unique_fps_to_fix = list(
            {v.split(":")[0] for v in details_41}
        )
        # Limit fixes to the first 3 files to avoid excessive calls
        for fp in unique_fps_to_fix[:3]:
            await self.smart_fix(fp, 41)

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: set | None = None) -> dict[str, int]:
        """L1 cognition agent - operational only."""
        super().heal_repository()

        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L1 cognition - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
