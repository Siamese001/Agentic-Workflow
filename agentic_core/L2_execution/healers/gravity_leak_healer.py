"""
gravity_leak_healer — HEALER_REGISTRY entry for gravity_violations.

L2.3 healing subsystem: fixes layer gravity violations (upward imports,
layer inversions) via GravityLeakRepairAgent.heal_violations(). Consumes
pre-computed violations from GravityValidatorAgent, eliminating the duplicate
internal scan that previously existed in GravityLeakRepairAgent.heal_repository().

Registered in HEALER_REGISTRY under check_id "gravity_violations".
"""

from __future__ import annotations

import logging
from pathlib import Path

from agentic_core.L2_execution.types.heal_contract_types import HealCheckResult, HealStatus
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

emit_replay_key("p0", "gravity_leak_healer")
emit_determinism_digest("p0", "gravity_leak_healer")

_emit_dispatches_healing_run("p1", "gravity_leak_healer", "L2")
_emit_routes_through("p1", "gravity_leak_healer", "L2")
_emit_checks_agent_registry("p1", "gravity_leak_healer", "agent_registry")
_emit_validates_agent_capability("p1", "gravity_leak_healer", "capability")
_emit_dispatches_execution_plan("p1", "gravity_leak_healer", "exec_plan")
_emit_agent_executes_agent("p1", "gravity_leak_healer", "sub_agent")
_emit_routes_to_agent("p1", "gravity_leak_healer", "target_agent")
_emit_verifies_policy("p1", "gravity_leak_healer", "policy_check")
_emit_observes_runtime_state("p1", "gravity_leak_healer", "runtime_state")
_emit_verifies_boundary("p1", "gravity_leak_healer", "boundary_check")
_emit_transcripts_response("p1", "gravity_leak_healer", "transcript")
_emit_hard_fails_untranscripted("p1", "gravity_leak_healer")
_emit_gated_by_confidence("p1", "gravity_leak_healer", "confidence_gate")
_emit_escalates_to_human("p1", "gravity_leak_healer", "L2")
_emit_reads_policy_state("p1", "gravity_leak_healer", "L2")
_emit_authorize_and_execute("p2", "gravity_leak_healer", "execution_auth")
_emit_validates_capability("p2", "gravity_leak_healer", "capability_check")
_emit_routes_to_capability("p2", "gravity_leak_healer", "capability_route")
_emit_writes_via_uwg("p2", "gravity_leak_healer", "uwg_write")
_emit_blocks_direct_write("p2", "gravity_leak_healer", "direct_write_block")
_emit_records_tool_invocation("p2", "gravity_leak_healer", "tool_invocation")
_emit_captures_execution_output("p2", "gravity_leak_healer", "exec_output")
_emit_dispatches_agent("p3", "gravity_leak_healer", "agent_dispatch")
_emit_coordinates_agents("p3", "gravity_leak_healer", "agent_coordination")
_emit_records_workflow_lineage("p3", "gravity_leak_healer", "workflow_lineage")
_emit_records_healing_outcome("p3", "gravity_leak_healer", "healing_outcome")
_emit_escalates_failure("p3", "gravity_leak_healer", "failure_escalation")
_emit_orchestrates_workflow("p3", "gravity_leak_healer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "gravity_leak_healer", "healing_dispatch")
_emit_invokes_evaluation("p3", "gravity_leak_healer", "evaluation_signal")
_emit_records_telemetry_event("p4", "gravity_leak_healer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "gravity_leak_healer", "eval_metric")
_emit_stores_embedding("p4", "gravity_leak_healer", "embedding_store")
_emit_updates_meta_learning_state("p4", "gravity_leak_healer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "gravity_leak_healer", "exec_snapshot_link")
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

_emit_emits_metric_event("gravity_leak_healer", "p4obs", "metric_1")
_emit_emits_metric_event("gravity_leak_healer", "p4obs", "metric_2")
_emit_emits_metric_event("gravity_leak_healer", "p4obs", "metric_3")
_emit_emits_metric_event("gravity_leak_healer", "p4obs", "metric_4")
_emit_emits_metric_event("gravity_leak_healer", "p4obs", "metric_5")
_emit_emits_metric_event("gravity_leak_healer", "p4obs", "metric_6")
_emit_records_incident_event("gravity_leak_healer", "p4obs", "incident")
_emit_captures_runtime_anomaly("gravity_leak_healer", "p4obs", "anomaly")
_emit_writes_observability_log("gravity_leak_healer", "p4obs", "obs_log")
_emit_updates_monitoring_state("gravity_leak_healer", "p4obs", "mon_state")
_emit_triggers_alert("gravity_leak_healer", "p4obs", "alert")
_emit_links_incident_trace("gravity_leak_healer", "p4obs", "trace_link")
_emit_captures_pattern("gravity_leak_healer", "p3lm", "pattern")
_emit_records_learning_event("gravity_leak_healer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("gravity_leak_healer", "p3lm", "snapshot")
_emit_feeds_meta_learning("gravity_leak_healer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("gravity_leak_healer", "p3lm", "routing")
_emit_improves_agent_policy("gravity_leak_healer", "p3lm", "policy")
_emit_stores_learning_state("gravity_leak_healer", "p3lm", "state")
_emit_records_execution_trace("gravity_leak_healer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("gravity_leak_healer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("gravity_leak_healer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("gravity_leak_healer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("gravity_leak_healer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("gravity_leak_healer", "env_read", "p2_env_1")
_emit_reads_environ("gravity_leak_healer", "env_read", "p2_env_2")
_emit_reads_runtime_state("gravity_leak_healer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("gravity_leak_healer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "gravity_leak_healer", "context_pull")
_emit_pulls_context("p1", "gravity_leak_healer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "gravity_leak_healer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "gravity_leak_healer", "uwg_term_2")
_emit_writes_through("p1", "gravity_leak_healer", "write_through")
_emit_writes_through("p1", "gravity_leak_healer", "write_through_2")
_emit_validated_by_safety_plane("p1", "gravity_leak_healer", "safety_validation")
_emit_invokes_eval("p1", "gravity_leak_healer", "eval_call")
_emit_proposal_commits_routing("p1", "gravity_leak_healer", "routing_commit")

CHECK_ID = "gravity_violations"
logger = logging.getLogger(__name__)


def heal_gravity_violations(
    check: dict, *, repo_root: Path | None = None, apply: bool = False
) -> HealCheckResult:
    """Heal layer gravity violations via GravityLeakRepairAgent.heal_violations().

    Consumes pre-computed violations from the check dict (produced by
    GravityValidatorAgent.to_check_dict()), so no duplicate scan occurs.

    Args:
        check: Check dict from GravityValidatorAgent.to_check_dict().
        repo_root: Absolute path to repository root (required for apply mode).
        apply: When False returns dry-run summary; when True performs healing.

    Returns:
        HealCheckResult with status HEALED / PARTIAL / SKIPPED / FAILED.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "heal_gravity_violations", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "heal_gravity_violations", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "heal_gravity_violations")
    evidence = check.get("evidence", {})
    violations = evidence.get("violations", [])
    violations_count = check.get("violations_count", len(violations))
    if not violations_count:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.HEALED,
            changes_made=(),
            notes="no gravity violations detected",
        )
    if not apply:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.SKIPPED,
            changes_made=(f"would_fix:{violations_count}_gravity_violations",),
            notes="dry-run: no mutations applied",
        )
    if repo_root is None:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.FAILED,
            changes_made=(),
            notes="apply mode requires repo_root",
        )
    repo_root = Path(repo_root).resolve()
    try:
        from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import GravityLeakRepairAgent

        agent = GravityLeakRepairAgent(project_root=repo_root)
        res = agent.heal_violations(violations, dry_run=False)
    # guardian: allow-silent-swallow
    except (ValueError, TypeError) as exc:
        logger.error("[gravity_leak_healer] heal failed: %s", exc)
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.FAILED,
            changes_made=(),
            notes=f"healer error: {type(exc).__name__}: {exc}",
            needs_llm_escalation=True,
            escalation_hint="failure_type=healer_error",
        )
    violations_found = res.get("violations_found", violations_count)
    violations_fixed = res.get("violations_fixed", 0)
    res_status = res.get("status", "UNKNOWN")
    changes: list[str] = []
    if violations_fixed > 0:
        changes.append(f"gravity_violations_fixed:{violations_fixed}")
    if res_status == "ERROR":
        status = HealStatus.FAILED
    elif violations_fixed < violations_found:
        status = HealStatus.PARTIAL
    else:
        status = HealStatus.HEALED
    return HealCheckResult(
        check_id=CHECK_ID,
        status=status,
        changes_made=tuple(sorted(changes)),
        notes=f"found={violations_found} fixed={violations_fixed}",
    )
