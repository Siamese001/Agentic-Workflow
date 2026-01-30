# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, workflow
from __future__ import annotations

import importlib  # AUTO-INJECTED BY GRAVITY HEALER
from dataclasses import dataclass

# This boosts alignment detection — review and integrate appropriately
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
GenerativeGuardAgent - Detects and removes runaway generated files.

KEYS: 45 (Dead Code/Runaway Generation)
ROLE: The Watchdog. Identifies and deletes recursively-generated files.
Extracted from CanonHealerAgent.py for one-file-per-agent pattern.
"""
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any
from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin

# GRAVITY VIOLATION: from apps_shared.base_agents.canon_base_agent_interface import CanonBaseAgentInterface (MOVED to agentic_core.utils.core_extensions)
# GRAVITY FIXED (Upward Leak): from agentic_core.base_agents.mcp_hardened_mixin import mcp_hardened_mixin
_mod = importlib.import_module("agentic_core.L5_safety.guardrails.mcp_hardened_mixin")
MCPHardenedMixin = _mod.MCPHardenedMixin

# Import CanonBaseAgentInterface
try:
    from agentic_core.base_agents.canon_base_agent_interface import CanonBaseAgentInterface
except ImportError:
    # Fallback if not available
    class CanonBaseAgentInterface:
        pass


try:
    from agentic_core.L5_safety.validators.structure_blueprint import (
        AGENT_DISCOVERY_JSON,
        AGENT_DISCOVERY_MANIFEST_JSON,
        AGENTIC_CORE_DIR,
        DASHBOARD_DIR,
        L0_MAINTENANCE_DIR,
        L1_COGNITION_DIR,
        L2_EXECUTION_DIR,
        L3_ORCHESTRATION_DIR,
        L4_STATE_DIR,
        L5_SAFETY_DIR,
        L6_OBSERVABILITY_DIR,
        SCRIPTS_DIR,
        TESTS_DIR,
        get_validated_project_root,
    )
except ImportError:
    # Fallback defaults
    from pathlib import Path

    AGENT_DISCOVERY_JSON = "agent_discovery_full.json"
    AGENT_DISCOVERY_MANIFEST_JSON = "agent_discovery_manifest.json"
    _root = Path(__file__).resolve().parent.parent.parent.parent
    AGENTIC_CORE_DIR = _root / "agentic_core"
    SCRIPTS_DIR = _root / "scripts"
    TESTS_DIR = _root / "tests"
    DASHBOARD_DIR = _root / "agentic_core" / "L6_observability" / "dashboards"
    L0_MAINTENANCE_DIR = _root / "agentic_core" / "L0_maintenance"
    L1_COGNITION_DIR = _root / "agentic_core" / "L1_cognition"
    L2_EXECUTION_DIR = _root / "agentic_core" / "L2_execution"
    L3_ORCHESTRATION_DIR = _root / "agentic_core" / "L3_orchestration"
    L4_STATE_DIR = _root / "agentic_core" / "L4_state"
    L5_SAFETY_DIR = _root / "agentic_core" / "L5_safety"
    L6_OBSERVABILITY_DIR = _root / "agentic_core" / "L6_observability"

    def get_validated_project_root() -> Path:
        return _root


# Excluded directories for file scanning
EXCLUDED_DIRS = [
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    ".vscode",
    ".idea",
    ".DS_Store",
    ".mypy_cache",
    ".pytest_cache",
    "htmlcov",
    "site-packages",
    "docs",
    TESTS_DIR,
    "temp",
    "tmp",
    "log",
    "logs",
]


@dataclass
class GenerativeGuardAgent(
    SovereignBaseAgent,
    SubatomicTestingMixin,
    HealerMixin,
    CanonBaseAgentInterface,
    MCPHardenedMixin,
):
    """
    KEYS: 45 (Dead Code/Runaway Generation)
    ROLE: The Watchdog. Identifies and deletes recursively-generated files.

    Detects files matching runaway generation patterns:
    - *_copy*.py
    - *_backup*.py
    - *_old*.py
    - *_temp*.py
    """

    def __init__(self, ctx: Any = None) -> None:
        """Initialize the instance."""
        self.impl = None  # CanonBaseAgent is abstract, skip instantiation
        self.ctx = ctx
        self.name = self.__class__.__name__
        self.Logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.GENERATIVE_PATTERNS = [
            r"_copy\d*\.py$",
            r"_backup\d*\.py$",
            r"_old\d*\.py$",
            r"_temp\d*\.py$",
        ]

    async def execute(self, goal: str = None, context: dict[str, Any] = None) -> dict[str, Any]:
        """Execute guard checks - maintains backward compatibility."""
        await self._execute_guard()
        return {"status": "completed", "agent": self.name}

    def get_capabilities(self) -> list[str]:
        """Return agent capabilities."""
        return ["runaway_detection", "file_cleanup", "pattern_matching"]

    def validate_state(self) -> bool:
        """Validate agent state."""
        return self.ctx is not None

    async def _execute_guard(self) -> Any:
        """Scan for and optionally purge runaway generated files."""
        print(f"\n[>>>] {self.name} ACTIVATED: Checking Generative Policy...")
        violations = []

        project_root = getattr(self.ctx, "project_root", ".")

        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            violations.extend(self._find_runaway_violations_in_dir(root, files))

        if violations:
            self._process_found_violations(violations)
        else:
            print("   [OK] No runaway generation detected.")
            self.ctx.report(self.name, 45, True, [])
            self.ctx.signals.add("GENERATIVE_CLEAN")

    def _purge_single_file(self, file_path: str) -> Any:
        """Helper to attempt purging a single file and report."""
        try:
            os.remove(file_path)
            print(f"         DELETED: {file_path}")
        except OSError as e:
            print(f"         [X] Failed to delete {file_path}: {e}", file=sys.stderr)

    def _process_found_violations(self, violations: list[str]) -> Any:
        """Helper to process and optionally purge detected runaway files."""
        print(f"   🛑 RUNAWAY GENERATION DETECTED ({len(violations)} files).")
        self.ctx.report(self.name, 45, False, violations)

        purge_runaway = "--purge-runaway" in sys.argv
        if not purge_runaway:
            self.ctx.signals.add("GENERATIVE_FAIL")
            print("      Hint: Run with '--purge-runaway' to delete these files.")
        else:
            print("      🗑️  Purging runaway generated files...")
            for file_path in violations:
                self._purge_single_file(file_path)
            self.ctx.signals.add("GENERATIVE_CLEAN")

    def _is_runaway_file(self, normalized_file_path: str) -> bool:
        """Helper to check if a file path matches any runaway pattern."""
        for pattern in self.GENERATIVE_PATTERNS:
            if re.search(pattern, normalized_file_path):
                return True
        return False

    def _find_runaway_violations_in_dir(self, root: str, files: list[str]) -> list[str]:
        """Helper to find runaway violations within a specific directory."""
        violations_in_dir = []
        for file in files:
            file_path = os.path.join(root, file)
            normalized_file_path = Path(file_path).as_posix()

            if self._is_runaway_file(normalized_file_path):
                violations_in_dir.append(file_path)
        return violations_in_dir

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
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

    def heal(self, violation: dict) -> dict:
        """Heal generative guard violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (runaway_generation)
                - path: Path to the runaway file
                - pattern: Pattern that matched

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        path = violation.get("path", "")

        if path:
            try:
                import os

                if os.path.exists(path):
                    os.remove(path)
                    return {"violations_fixed": 1, "violations_found": 1, "errors": 0, "skipped": 0}
            except Exception:
                return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}

        return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
