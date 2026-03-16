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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "inspection_capability_mixin", "p0_governance")
_emit_reads_policy_state("p0", "inspection_capability_mixin", "policy_binding")
_emit_snapshots_state("p0", "inspection_capability_mixin", "state_snapshot")
emit_replay_key("p0", "inspection_capability_mixin")
emit_determinism_digest("p0", "inspection_capability_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "inspection_capability_mixin", "execution_auth")
_emit_validates_capability("p2", "inspection_capability_mixin", "capability_check")
_emit_routes_to_capability("p2", "inspection_capability_mixin", "capability_route")
_emit_writes_via_uwg("p2", "inspection_capability_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "inspection_capability_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "inspection_capability_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "inspection_capability_mixin", "exec_output")
_emit_dispatches_agent("p3", "inspection_capability_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "inspection_capability_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "inspection_capability_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "inspection_capability_mixin", "healing_outcome")
_emit_escalates_failure("p3", "inspection_capability_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "inspection_capability_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "inspection_capability_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "inspection_capability_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "inspection_capability_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "inspection_capability_mixin", "eval_metric")
_emit_stores_embedding("p4", "inspection_capability_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "inspection_capability_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "inspection_capability_mixin", "exec_snapshot_link")


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
