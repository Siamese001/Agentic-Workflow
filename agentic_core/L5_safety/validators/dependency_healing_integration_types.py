"""
Dependency Healing Integration Module - Phase 1 Foundation

Registers DependencyPruningAgent as a healing strategy in the
HealingSovereignOrchestrator.

This module adapts the DependencyPruningAgent to the HealingStrategy
protocol, enabling automatic cleanup of unused dependencies.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Protocol

Logger = logging.getLogger(__name__)


class HealingStrategyProtocol(Protocol):
    """Protocol for healing strategies."""

    def can_heal(self, violation: dict) -> bool:
        """Check if this strategy can heal the violation."""
        ...

    def heal(self, violation: dict, context: dict) -> dict:
        """Execute healing and return result."""
        ...


class DependencyPruningStrategy:
    """
    Healing strategy for unused dependency violations.

    Wraps DependencyPruningAgent to detect and optionally remove
    unused Python dependencies from requirements.txt.
    """

    # Violation types this strategy can handle
    SUPPORTED_VIOLATIONS = frozenset(
        {
            "unused_dependency",
            "dependency_bloat",
            "requirements_cleanup",
            "dependency_audit",
        }
    )

    def __init__(self, project_root: Path | None = None) -> None:
        """
        Initialize the dependency pruning strategy.

        Args:
            project_root: Root directory of the project (defaults to cwd)
        """
        self.project_root = project_root or Path.cwd()
        self._agent = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization to avoid import cycles."""
        if self._initialized:
            return

        try:
            from agentic_core.L5_safety.guardrails.DependencyPruningAgent import (
                DependencyPruningAgent,
            )

            # Create a mock context for the agent
            class MockContext:
                def report(self, msg: str) -> None:
                    Logger.debug(f"[DependencyPruning] {msg}")

            self._agent = DependencyPruningAgent(project_root=self.project_root, ctx=MockContext())
            self._initialized = True
        except ImportError as e:
            Logger.warning(f"[DependencyPruningStrategy] Could not import agent: {e}")
            self._initialized = True

    def can_heal(self, violation: dict) -> bool:
        """
        Check if this strategy can handle the violation.

        Args:
            violation: Violation details with 'type' key

        Returns:
            True if this strategy can handle the violation type
        """
        violation_type = violation.get("type", "")
        return violation_type in self.SUPPORTED_VIOLATIONS

    def heal(self, violation: dict, context: dict) -> dict:
        """
        Prune unused dependencies.

        Args:
            violation: Violation details (may include specific package)
            context: Healing context (may include dry_run flag)

        Returns:
            dict with healing results
        """
        self._ensure_initialized()

        if self._agent is None:
            return {
                "success": True,
                "unused_found": 0,
                "removed": 0,
                "status": "agent_unavailable",
            }

        try:
            # Use dry_run from context or default to True for safety
            self._agent.dry_run = context.get("dry_run", True)

            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(self._agent.execute())
            finally:
                loop.close()

            unused_found = result.get("unused_found", 0)
            removed = result.get("removed", 0)

            return {
                "success": removed > 0 or unused_found == 0,
                "unused_found": unused_found,
                "removed": removed,
                "dry_run": self._agent.dry_run,
            }

        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"[DependencyPruningStrategy] Healing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "unused_found": 0,
                "removed": 0,
            }


# Global strategy instance (lazy-initialized)
_dependency_strategy: DependencyPruningStrategy | None = None


def get_dependency_strategy(project_root: Path | None = None) -> DependencyPruningStrategy:
    """Get or create the dependency pruning strategy instance."""
    global _dependency_strategy
    if _dependency_strategy is None:
        _dependency_strategy = DependencyPruningStrategy(project_root)
    return _dependency_strategy


def register_dependency_healing(project_root: Path | None = None) -> dict[str, Any]:
    """
    Register dependency pruning as a healing strategy.

    Args:
        project_root: Optional project root path

    Returns:
        dict with registration status
    """
    registered = []
    errors = []

    try:
        from agentic_core.L5_safety.validators.healing_sovereign_orchestrator_types import (
            get_healing_orchestrator,
        )

        orchestrator = get_healing_orchestrator()

        try:
            orchestrator.register_strategy(
                "dependency_pruning", get_dependency_strategy(project_root)
            )
            registered.append("dependency_pruning")
        # guardian: allow-silent-swallow
        except Exception as e:
            errors.append(f"dependency_pruning: {e}")

        Logger.info(f"[Dependency Integration] Registered {len(registered)} strategies")

    except ImportError as e:
        errors.append(f"HealingSovereignOrchestrator import failed: {e}")
        Logger.warning(f"[Dependency Integration] Could not import orchestrator: {e}")

    return {
        "registered": registered,
        "errors": errors,
        "success": len(errors) == 0,
    }


def get_integration_status() -> dict[str, Any]:
    """Get the current status of dependency healing integration."""
    return {
        "dependency_strategy_initialized": _dependency_strategy is not None,
        "strategies_available": ["dependency_pruning"],
        "supported_violations": list(DependencyPruningStrategy.SUPPORTED_VIOLATIONS),
    }
