"""Dependency Pruning Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.dependency_pruning_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.dependency_pruning_util import (
    DependencyPruner as _DependencyPruner,
    PruningResult,
    find_unused_deptry,
    remove_from_requirements_txt,
)


class DependencyPruningAgent(SovereignBaseAgent):
    """
    DEPRECATED: Dependency Pruning Agent - now delegates to dependency_pruning_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L5_safety.utils.dependency_pruning_util directly.
    """

    def __init__(self, project_root: Path, ctx: Any | None = None) -> None:
        """Initialize DependencyPruningAgent (deprecated, use dependency_pruning_util instead)."""
        super().__init__(name="DependencyPruningAgent", layer="L5")

        warnings.warn(
            "DependencyPruningAgent is deprecated. Use agentic_core.L5_safety.utils.dependency_pruning_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.project_root: Path = Path(project_root)
        self.ctx: Any = ctx
        self.dry_run: bool = True
        self._pruner = _DependencyPruner(self.project_root, self.dry_run)

    def _find_unused_deptry(self) -> list[str]:
        """Find unused dependencies using deptry."""
        return find_unused_deptry(self.project_root)

    def _remove_from_requirements_txt(self, unused: list[str]) -> dict[str, Any]:
        """Remove unused packages from requirements.txt."""
        requirements_path = self.project_root / "requirements.txt"
        return remove_from_requirements_txt(unused, requirements_path, self.dry_run)

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute L5 safety healing operations."""
        self.dry_run = dry_run
        self._pruner.dry_run = dry_run
        
        result = self._pruner.heal_repository(dry_run)
        return result

    async def execute(self) -> dict[str, Any]:
        """Scan for and optionally remove unused dependencies."""
        result = self._pruner.prune()
        return result.to_dict()

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal dependency pruning violations."""
        return self._pruner.heal(violation)
