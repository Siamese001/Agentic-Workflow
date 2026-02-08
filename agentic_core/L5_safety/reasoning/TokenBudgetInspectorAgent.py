"""
TokenBudgetInspectorAgent - Diagnostics for token budget consumption.

Refactored: 2026-02-08 (Cluster 1B — InspectionCapability extraction)
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.base_agents.decorators import standard_heal

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.inspection_capability import (
    DiagnosticReport,
    InspectionCapability,
)
from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin

Logger: Any = logging.getLogger(__name__)


class TokenBudgetInspectorAgent(
    InspectionCapability,
    SubatomicTestingMixin,
    SovereignBaseAgent,
):
    """Diagnostics inspector for token budget consumption."""

    INSPECTION_LOG_PREFIX = "Running token budget diagnostics..."

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the inspector."""
        super().__init__()
        self.config = config or {}
        Logger.info("Initialized %s", self.__class__.__name__)

    def perform_checks(
        self,
        target: Any,
        context: dict[str, Any] | None = None,
    ) -> tuple[list[str], dict[str, Any]]:
        """Inspect a target object for structural issues."""
        issues: list[str] = []
        metrics: dict[str, Any] = {}

        if target is None:
            issues.append("Target is null")
        elif isinstance(target, dict):
            metrics["field_count"] = len(target)
        elif isinstance(target, list):
            metrics["item_count"] = len(target)

        metrics["type"] = type(target).__name__

        return issues, metrics

    def diagnose(self, target: Any, context: dict[str, Any] | None = None) -> DiagnosticReport:
        """Run diagnostics via InspectionCapability harness.

        Returns DiagnosticReport (adapter) to preserve the pre-refactor
        external contract.
        """
        result = self.run_inspection(target, context)
        return result.to_diagnostic_report()

    @standard_heal
    def heal_repository(self, **kwargs: Any) -> dict[str, Any]:
        """Invoke healing chain via super()."""
        return super().heal_repository(**kwargs)

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by TokenBudgetInspectorAgent."""
        return self.make_heal_result(violation)


def diagnose(target: Any, config: dict[str, Any] | None = None) -> DiagnosticReport:
    """Convenience function for diagnostics."""
    return TokenBudgetInspectorAgent(config).diagnose(target)
