"""Shared core for L5 Safety code-tool-runner agents.

Consolidation artifact: extracts the common infrastructure shared by
CodeFormatterAgent and UnusedCleanupAgent (Cluster 6, code_sim=0.771).

Both agents wrap external CLI tools (Black/Ruff vs autoflake) with identical:
  - heal_repository() with cycle-detection + depth-limiting
  - heal() with standard_heal decorator pattern

This module provides CodeToolRunnerCapability — a **pure capability class**
that knows nothing about agents or SovereignBaseAgent. Consuming agents
compose it via multiple inheritance:

    class CodeFormatterAgent(CodeToolRunnerCapability, SovereignBaseAgent):
        ...

[REFACTORED 2026-02-08] Removed SovereignBaseAgent inheritance to fix
Diamond Problem risk. See critique in validation_report.md §1.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.L0_maintenance.utils.timeout_decorator_util import timeout
from agentic_core.L5_safety.utils.decorators_util import standard_heal


class CodeToolRunnerCapability:
    """Pure capability mixin for L5 code-tool-runner agents.

    Provides:
        - heal_repository() with cycle-detection and depth-limiting
        - heal() template that delegates to execute()

    Expects the consuming dataclass to provide:
        - self.project_root: Path
        - self.ctx: Any

    Subclasses MUST implement:
        - execute(file_path: str) -> dict[str, Any]
    """

    async def execute(self, file_path: str) -> dict[str, Any]:
        """Run the tool on a single file.  Must be overridden by subclasses."""
        raise NotImplementedError

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
    ) -> dict[str, int]:
        """Execute L5 safety healing operations.

        This is an operational agent - no repository healing required.
        Implements cycle detection and depth limiting.

        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.

        Returns:
            Dictionary with healing results: {"skipped": 1} for operational agents.
        """
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    def heal(self, violation: dict) -> dict:
        """Heal violations using standard_heal decorator pattern.

        Delegates to execute() for the actual tool invocation.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation
                - path: Path to the violating file

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        path = violation.get("path", "")

        try:
            if path:
                file_path = Path(path)
                if file_path.exists():
                    import asyncio

                    result = asyncio.get_event_loop().run_until_complete(
                        self.execute(str(file_path)),
                    )
                    return {
                        "violations_fixed": 1 if result.get("healed") else 0,
                        "violations_found": 1,
                        "errors": 0,
                        "skipped": 0,
                    }
            return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
        # guardian: allow-silent-swallow
        except Exception:
            return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}


# Backward-compat alias for existing imports
CodeToolRunnerMixin = CodeToolRunnerCapability
