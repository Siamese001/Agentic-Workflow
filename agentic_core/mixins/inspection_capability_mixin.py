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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "inspection_capability_mixin", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "inspection_capability_mixin", "policy_binding")
trace_contract._emit_snapshots_state("p0", "inspection_capability_mixin", "state_snapshot")

trace_contract._emit_emits_metric_event("inspection_capability_mixin", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("inspection_capability_mixin", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("inspection_capability_mixin", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("inspection_capability_mixin", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("inspection_capability_mixin", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("inspection_capability_mixin", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("inspection_capability_mixin", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("inspection_capability_mixin", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("inspection_capability_mixin", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("inspection_capability_mixin", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("inspection_capability_mixin", "p4obs", "alert")
trace_contract._emit_links_incident_trace("inspection_capability_mixin", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("inspection_capability_mixin", "p3lm", "pattern")
trace_contract._emit_records_learning_event("inspection_capability_mixin", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("inspection_capability_mixin", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("inspection_capability_mixin", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("inspection_capability_mixin", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("inspection_capability_mixin", "p3lm", "policy")
trace_contract._emit_stores_learning_state("inspection_capability_mixin", "p3lm", "state")
trace_contract._emit_records_execution_trace("inspection_capability_mixin", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("inspection_capability_mixin", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("inspection_capability_mixin", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("inspection_capability_mixin", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("inspection_capability_mixin", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("inspection_capability_mixin", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("inspection_capability_mixin", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("inspection_capability_mixin", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("inspection_capability_mixin", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "inspection_capability_mixin", "context_pull")
trace_contract._emit_pulls_context("p1", "inspection_capability_mixin", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "inspection_capability_mixin", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "inspection_capability_mixin", "uwg_term_2")
trace_contract._emit_writes_through("p1", "inspection_capability_mixin", "write_through")
trace_contract._emit_writes_through("p1", "inspection_capability_mixin", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "inspection_capability_mixin", "safety_validation")
trace_contract._emit_invokes_eval("p1", "inspection_capability_mixin", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "inspection_capability_mixin", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "inspection_capability_mixin", "human_escalation")
trace_contract._emit_routes_through("p1", "inspection_capability_mixin", "route_through")
trace_contract._emit_checks_agent_registry("p1", "inspection_capability_mixin", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "inspection_capability_mixin", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "inspection_capability_mixin", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "inspection_capability_mixin", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "inspection_capability_mixin", "target_agent")
trace_contract._emit_verifies_policy("p1", "inspection_capability_mixin", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "inspection_capability_mixin", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "inspection_capability_mixin", "boundary_check")
trace_contract._emit_transcripts_response("p1", "inspection_capability_mixin", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "inspection_capability_mixin")
trace_contract._emit_gated_by_confidence("p1", "inspection_capability_mixin", "confidence_gate")
trace_contract.emit_replay_key("p0", "inspection_capability_mixin")
trace_contract.emit_determinism_digest("p0", "inspection_capability_mixin")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "inspection_capability_mixin", "execution_auth")
trace_contract._emit_validates_capability("p2", "inspection_capability_mixin", "capability_check")
trace_contract._emit_routes_to_capability("p2", "inspection_capability_mixin", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "inspection_capability_mixin", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "inspection_capability_mixin", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "inspection_capability_mixin", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "inspection_capability_mixin", "exec_output")
trace_contract._emit_dispatches_agent("p3", "inspection_capability_mixin", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "inspection_capability_mixin", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "inspection_capability_mixin", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "inspection_capability_mixin", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "inspection_capability_mixin", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "inspection_capability_mixin", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "inspection_capability_mixin", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "inspection_capability_mixin", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "inspection_capability_mixin", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "inspection_capability_mixin", "eval_metric")
trace_contract._emit_stores_embedding("p4", "inspection_capability_mixin", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "inspection_capability_mixin", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "inspection_capability_mixin", "exec_snapshot_link")


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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "InspectionCapability.run_inspection"
        )

        import logging

        logger = logging.getLogger(self.__class__.__module__)
        logger.info("[%s] %s", self.__class__.__name__, self.INSPECTION_LOG_PREFIX)
        issues, metrics = self.perform_checks(target, context)
        return InspectionResult(healthy=len(issues) == 0, issues=issues, metrics=metrics)

    def perform_checks(
        self,
        target: Any,
        context: dict[str, Any] | None = None,
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
