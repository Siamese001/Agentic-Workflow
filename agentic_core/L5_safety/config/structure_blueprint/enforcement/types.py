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
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "types")
emit_determinism_digest("p0", "types")

_emit_dispatches_healing_run("p1", "types", "L5")
_emit_routes_through("p1", "types", "L5")
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
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "make_result")
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
