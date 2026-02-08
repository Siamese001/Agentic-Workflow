"""
DagRuntimeInspectorAgent - Runtime diagnostics for DAG execution graphs.

Refactored: 2026-02-08 (Cluster 1B — InspectionCapability extraction)
"""

from typing import Any

from agentic_core.base_agents.decorators import standard_heal

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.atomic_execution_mixin import AtomicExecutionMixin
from agentic_core.mixins.inspection_capability import (
    InspectionCapability,
    InspectionResult,
)
from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin


class DagRuntimeInspectorAgent(
    InspectionCapability,
    AtomicExecutionMixin,
    SubatomicTestingMixin,
    SovereignBaseAgent,
):
    """Runtime diagnostics inspector for DAG execution graphs."""

    INSPECTION_LOG_PREFIX = "Running DAG runtime diagnostics..."

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the inspector."""
        super().__init__()
        self.config = config or {}

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

    def diagnose(self, target: Any, context: dict[str, Any] | None = None) -> InspectionResult:
        """Run diagnostics via InspectionCapability harness."""
        return self.run_inspection(target, context)

    @standard_heal
    def heal_repository(self, **kwargs: Any) -> dict[str, Any]:
        """Invoke healing chain via super()."""
        return super().heal_repository(**kwargs)

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by DagRuntimeInspectorAgent."""
        return self.make_heal_result(violation)


def diagnose(target: Any, config: dict[str, Any] | None = None) -> InspectionResult:
    """Convenience function for diagnostics."""
    inspector = DagRuntimeInspectorAgent(config)
    return inspector.diagnose(target)
