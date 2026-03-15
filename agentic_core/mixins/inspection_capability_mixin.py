"""
InspectionCapability — Pure capability mixin for inspector agents.

Extracts the shared inspection harness that all inspector agents repeat:
  - Structured result object (InspectionResult)
  - Template method run_inspection() with logging
  - Abstract perform_checks() hook for domain-specific logic
  - Standard heal stub generation

The domain-specific check logic remains in each agent's perform_checks() override.
Agents compose this via multiple inheritance alongside SovereignBaseAgent.

    class SomeInspectorAgent(InspectionCapability, SovereignBaseAgent):
        INSPECTION_LOG_PREFIX = "Inspecting something..."

        def perform_checks(self, target, context=None):
            issues, metrics = [], {}
            ...  # domain-specific logic
            return issues, metrics

RESPONSIBILITY COHESION: This capability must NOT contain domain-specific words.
It only knows about "checks", "issues", "metrics", and "results".

[CREATED 2026-02-08] Cluster 1B extraction per Pure Harness pattern.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass
class InspectionResult:
    """Structured result from an inspection run.

    Attributes:
        healthy: Whether the inspected target passed all checks.
        issues: List of issue description strings (empty means healthy).
        metrics: Dictionary of observed metrics from the inspection.
    """

    healthy: bool = True
    issues: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


class InspectionCapability:
    """Pure capability mixin for inspector agents.

    Provides:
        - run_inspection(target, context): Template method with logging
        - perform_checks(target, context): Abstract hook for domain logic
        - make_heal_result(violation): Standard heal stub generator

    Subclasses MUST:
        - Set INSPECTION_LOG_PREFIX (e.g., "Running checks...")
        - Override perform_checks(target, context) with domain logic
    """

    INSPECTION_LOG_PREFIX: ClassVar[str] = "Running inspection..."

    def run_inspection(self, target: Any, context: dict[str, Any] | None = None) -> InspectionResult:
        """Template method: log entry, perform checks, build result.

        Calls self.perform_checks() and wraps the output in an
        InspectionResult. Logs via Logger if available.

        Args:
            target: The object to inspect.
            context: Optional context dictionary for the inspection.

        Returns:
            InspectionResult with healthy flag, issues, and metrics.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "InspectionCapability.run_inspection")

        import logging

        logger = logging.getLogger(self.__class__.__module__)
        logger.info("[%s] %s", self.__class__.__name__, self.INSPECTION_LOG_PREFIX)
        issues, metrics = self.perform_checks(target, context)
        return InspectionResult(healthy=len(issues) == 0, issues=issues, metrics=metrics)

    def perform_checks(
        self, target: Any, context: dict[str, Any] | None = None
    ) -> tuple[list[str], dict[str, Any]]:
        """Execute domain-specific inspection logic.

        Default implementation provides structural type-checking and metrics
        collection. Subclasses SHOULD override this with domain-specific logic.

        Args:
            target: The object to inspect.
            context: Optional context dictionary.

        Returns:
            Tuple of (issues list, metrics dict).
        """
        issues: list[str] = []
        metrics: dict[str, Any] = {}
        if target is None:
            issues.append("Target is null")
        elif isinstance(target, dict):
            metrics["field_count"] = len(target)
        elif isinstance(target, list):
            metrics["item_count"] = len(target)
        metrics["type"] = type(target).__name__
        return (issues, metrics)

    def make_heal_result(self, violation: dict[str, Any], *, status: str = "skipped") -> dict[str, Any]:
        """Generate a standard heal stub result.

        Args:
            violation: The violation dict being healed.
            status: Heal status (default "skipped").

        Returns:
            Canonical heal result dict.
        """
        violation_type = violation.get("type", "unknown")
        return {
            "status": status,
            "details": f"{self.__class__.__name__} heal() not yet implemented for {violation_type}",
            "artifacts": [],
            "errors": [],
        }
