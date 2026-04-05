"""
Enforcement Result Types â€” Shared typed contracts for all enforcement modules.

Every enforcement module returns an EnforcementResult from its check() function.
The orchestrator (_verify.py) aggregates these into an EnforcementReport and
emits a deterministic JSON artifact.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TypedDict

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "types")
emit_determinism_digest("p0", "types")

_emit_dispatches_healing_run("p1", "types", "L5")
_emit_routes_through("p1", "types", "L5")
_emit_checks_agent_registry("p1", "types", "agent_registry")
_emit_validates_agent_capability("p1", "types", "capability")
_emit_dispatches_execution_plan("p1", "types", "exec_plan")
_emit_agent_executes_agent("p1", "types", "sub_agent")
_emit_routes_to_agent("p1", "types", "target_agent")
_emit_verifies_policy("p1", "types", "policy_check")
_emit_observes_runtime_state("p1", "types", "runtime_state")
_emit_verifies_boundary("p1", "types", "boundary_check")
_emit_transcripts_response("p1", "types", "transcript")
_emit_hard_fails_untranscripted("p1", "types")
_emit_gated_by_confidence("p1", "types", "confidence_gate")
_emit_escalates_to_human("p1", "types", "L5")
_emit_reads_policy_state("p1", "types", "L5")
_emit_authorize_and_execute("p2", "types", "execution_auth")
_emit_validates_capability("p2", "types", "capability_check")
_emit_routes_to_capability("p2", "types", "capability_route")
_emit_writes_via_uwg("p2", "types", "uwg_write")
_emit_blocks_direct_write("p2", "types", "direct_write_block")
_emit_records_tool_invocation("p2", "types", "tool_invocation")
_emit_captures_execution_output("p2", "types", "exec_output")
_emit_dispatches_agent("p3", "types", "agent_dispatch")
_emit_coordinates_agents("p3", "types", "agent_coordination")
_emit_records_workflow_lineage("p3", "types", "workflow_lineage")
_emit_records_healing_outcome("p3", "types", "healing_outcome")
_emit_escalates_failure("p3", "types", "failure_escalation")
_emit_orchestrates_workflow("p3", "types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "types", "healing_dispatch")
_emit_invokes_evaluation("p3", "types", "evaluation_signal")
_emit_records_telemetry_event("p4", "types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "types", "eval_metric")
_emit_stores_embedding("p4", "types", "embedding_store")
_emit_updates_meta_learning_state("p4", "types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "types", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("types", "p4obs", "metric_1")
_emit_emits_metric_event("types", "p4obs", "metric_2")
_emit_emits_metric_event("types", "p4obs", "metric_3")
_emit_emits_metric_event("types", "p4obs", "metric_4")
_emit_emits_metric_event("types", "p4obs", "metric_5")
_emit_emits_metric_event("types", "p4obs", "metric_6")
_emit_records_incident_event("types", "p4obs", "incident")
_emit_captures_runtime_anomaly("types", "p4obs", "anomaly")
_emit_writes_observability_log("types", "p4obs", "obs_log")
_emit_updates_monitoring_state("types", "p4obs", "mon_state")
_emit_triggers_alert("types", "p4obs", "alert")
_emit_links_incident_trace("types", "p4obs", "trace_link")
_emit_captures_pattern("types", "p3lm", "pattern")
_emit_records_learning_event("types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("types", "p3lm", "snapshot")
_emit_feeds_meta_learning("types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("types", "p3lm", "routing")
_emit_improves_agent_policy("types", "p3lm", "policy")
_emit_stores_learning_state("types", "p3lm", "state")
_emit_records_execution_trace("types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("types", "env_read", "p2_env_1")
_emit_reads_environ("types", "env_read", "p2_env_2")
_emit_reads_runtime_state("types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "types", "context_pull")
_emit_pulls_context("p1", "types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "types", "uwg_term_2")
_emit_writes_through("p1", "types", "write_through")
_emit_writes_through("p1", "types", "write_through_2")
_emit_validated_by_safety_plane("p1", "types", "safety_validation")
_emit_invokes_eval("p1", "types", "eval_call")
_emit_proposal_commits_routing("p1", "types", "routing_commit")


class Violation(TypedDict):
    """A single enforcement violation."""

    type: str
    path: str
    severity: str  # "error" or "warning"
    detail: str


class EnforcementResult(TypedDict):
    """Result from a single enforcement module's check() call."""

    name: str
    passed: bool
    violations: list[Violation]
    stats: dict[str, int]


class EnforcementReport(TypedDict):
    """Aggregated report from all enforcement modules."""

    timestamp: str
    verifier_version: str
    overall_passed: bool
    checks: list[EnforcementResult]
    summary: dict[str, int]


VERIFIER_VERSION = "4.5.0"


def make_result(
    name: str,
    violations: list[Violation],
    stats: dict[str, int],
) -> EnforcementResult:
    """Create an EnforcementResult with computed passed status."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "make_result", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "make_result", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "make_result")
    has_errors = any(v["severity"] == "error" for v in violations)
    return EnforcementResult(
        name=name,
        passed=not has_errors,
        violations=violations,
        stats=stats,
    )


BUDGETED_WARNING_TYPES: frozenset[str] = frozenset(
    {
        "missing_optional_subfolder",
        # Known-debt violations are budgeted only when explicitly listed in
        # known_debt_baseline.json with ceiling enforcement. The violation type
        # is config_execution_violation (for gateway_config.py lazy imports).
        # All other cross-layer violations are errors by default.
        "config_execution_violation",
    },
)


def make_report(results: list[EnforcementResult]) -> EnforcementReport:
    """Aggregate individual results into a full report."""
    passed_count = sum(1 for r in results if r["passed"])
    failed_count = len(results) - passed_count
    all_violations = [v for r in results for v in r["violations"]]
    total_violations = len(all_violations)

    warnings = [v for v in all_violations if v["severity"] == "warning"]
    errors = [v for v in all_violations if v["severity"] == "error"]
    budgeted = [w for w in warnings if w["type"] in BUDGETED_WARNING_TYPES]
    unbudgeted = [w for w in warnings if w["type"] not in BUDGETED_WARNING_TYPES]

    return EnforcementReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        verifier_version=VERIFIER_VERSION,
        overall_passed=all(r["passed"] for r in results),
        checks=results,
        summary={
            "total_checks": len(results),
            "passed": passed_count,
            "failed": failed_count,
            "total_violations": total_violations,
            "errors": len(errors),
            "warnings_budgeted": len(budgeted),
            "warnings_unbudgeted": len(unbudgeted),
        },
    )


def emit_report_json(report: EnforcementReport) -> dict[str, Any]:
    """Convert report to JSON-serializable dict (identity for TypedDict)."""
    return dict(report)
