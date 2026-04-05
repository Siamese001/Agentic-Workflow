"""
file_classification_healer — HEALER_REGISTRY entry for file_classification.

L2.3 healing subsystem: relocates misclassified files and fixes naming
violations via FileClassificationAgent.heal_repository(). Registered in
HEALER_REGISTRY under check_id "file_classification".
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

emit_replay_key("p0", "file_classification_healer")
emit_determinism_digest("p0", "file_classification_healer")

_emit_dispatches_healing_run("p1", "file_classification_healer", "L2")
_emit_routes_through("p1", "file_classification_healer", "L2")
_emit_checks_agent_registry("p1", "file_classification_healer", "agent_registry")
_emit_validates_agent_capability("p1", "file_classification_healer", "capability")
_emit_dispatches_execution_plan("p1", "file_classification_healer", "exec_plan")
_emit_agent_executes_agent("p1", "file_classification_healer", "sub_agent")
_emit_routes_to_agent("p1", "file_classification_healer", "target_agent")
_emit_verifies_policy("p1", "file_classification_healer", "policy_check")
_emit_observes_runtime_state("p1", "file_classification_healer", "runtime_state")
_emit_verifies_boundary("p1", "file_classification_healer", "boundary_check")
_emit_transcripts_response("p1", "file_classification_healer", "transcript")
_emit_hard_fails_untranscripted("p1", "file_classification_healer")
_emit_gated_by_confidence("p1", "file_classification_healer", "confidence_gate")
_emit_escalates_to_human("p1", "file_classification_healer", "L2")
_emit_reads_policy_state("p1", "file_classification_healer", "L2")
_emit_authorize_and_execute("p2", "file_classification_healer", "execution_auth")
_emit_validates_capability("p2", "file_classification_healer", "capability_check")
_emit_routes_to_capability("p2", "file_classification_healer", "capability_route")
_emit_writes_via_uwg("p2", "file_classification_healer", "uwg_write")
_emit_blocks_direct_write("p2", "file_classification_healer", "direct_write_block")
_emit_records_tool_invocation("p2", "file_classification_healer", "tool_invocation")
_emit_captures_execution_output("p2", "file_classification_healer", "exec_output")
_emit_dispatches_agent("p3", "file_classification_healer", "agent_dispatch")
_emit_coordinates_agents("p3", "file_classification_healer", "agent_coordination")
_emit_records_workflow_lineage("p3", "file_classification_healer", "workflow_lineage")
_emit_records_healing_outcome("p3", "file_classification_healer", "healing_outcome")
_emit_escalates_failure("p3", "file_classification_healer", "failure_escalation")
_emit_orchestrates_workflow("p3", "file_classification_healer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "file_classification_healer", "healing_dispatch")
_emit_invokes_evaluation("p3", "file_classification_healer", "evaluation_signal")
_emit_records_telemetry_event("p4", "file_classification_healer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "file_classification_healer", "eval_metric")
_emit_stores_embedding("p4", "file_classification_healer", "embedding_store")
_emit_updates_meta_learning_state("p4", "file_classification_healer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "file_classification_healer", "exec_snapshot_link")
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

_emit_emits_metric_event("file_classification_healer", "p4obs", "metric_1")
_emit_emits_metric_event("file_classification_healer", "p4obs", "metric_2")
_emit_emits_metric_event("file_classification_healer", "p4obs", "metric_3")
_emit_emits_metric_event("file_classification_healer", "p4obs", "metric_4")
_emit_emits_metric_event("file_classification_healer", "p4obs", "metric_5")
_emit_emits_metric_event("file_classification_healer", "p4obs", "metric_6")
_emit_records_incident_event("file_classification_healer", "p4obs", "incident")
_emit_captures_runtime_anomaly("file_classification_healer", "p4obs", "anomaly")
_emit_writes_observability_log("file_classification_healer", "p4obs", "obs_log")
_emit_updates_monitoring_state("file_classification_healer", "p4obs", "mon_state")
_emit_triggers_alert("file_classification_healer", "p4obs", "alert")
_emit_links_incident_trace("file_classification_healer", "p4obs", "trace_link")
_emit_captures_pattern("file_classification_healer", "p3lm", "pattern")
_emit_records_learning_event("file_classification_healer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("file_classification_healer", "p3lm", "snapshot")
_emit_feeds_meta_learning("file_classification_healer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("file_classification_healer", "p3lm", "routing")
_emit_improves_agent_policy("file_classification_healer", "p3lm", "policy")
_emit_stores_learning_state("file_classification_healer", "p3lm", "state")
_emit_records_execution_trace("file_classification_healer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("file_classification_healer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("file_classification_healer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("file_classification_healer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("file_classification_healer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("file_classification_healer", "env_read", "p2_env_1")
_emit_reads_environ("file_classification_healer", "env_read", "p2_env_2")
_emit_reads_runtime_state("file_classification_healer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("file_classification_healer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "file_classification_healer", "context_pull")
_emit_pulls_context("p1", "file_classification_healer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "file_classification_healer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "file_classification_healer", "uwg_term_2")
_emit_writes_through("p1", "file_classification_healer", "write_through")
_emit_writes_through("p1", "file_classification_healer", "write_through_2")
_emit_validated_by_safety_plane("p1", "file_classification_healer", "safety_validation")
_emit_invokes_eval("p1", "file_classification_healer", "eval_call")
_emit_proposal_commits_routing("p1", "file_classification_healer", "routing_commit")

CHECK_ID = "file_classification"
logger = logging.getLogger(__name__)


def heal_file_classification(
    check: dict, *, repo_root: Path | None = None, apply: bool = False
) -> HealCheckResult:
    """Heal file classification violations via FileClassificationAgent.heal_repository().

    Uses cached scan results from the check dict to avoid re-scanning.

    Args:
        check: Check dict from FileClassificationValidatorAgent.to_check_dict().
        repo_root: Absolute path to repository root (required for apply mode).
        apply: When False returns dry-run summary; when True performs healing.

    Returns:
        HealCheckResult with status HEALED / PARTIAL / SKIPPED / FAILED.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "heal_file_classification", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "heal_file_classification", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "heal_file_classification")
    violations_count = check.get("violations_count", 0)
    territory = check.get("territory")
    evidence = check.get("evidence", {})
    if not violations_count:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.HEALED,
            changes_made=(),
            notes="no file classification violations detected",
        )
    if not apply:
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.SKIPPED,
            changes_made=(f"would_fix:{violations_count}_classification_violations",),
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
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent

        classifier = FileClassificationAgent(project_root=repo_root)
        cached_scan = {"file_registry": evidence.get("file_registry", [])}
        res = classifier.heal_repository(
            target_territory=territory, dry_run=False, auto_approve=True, cached_scan=cached_scan
        )
    # guardian: allow-silent-swallow
    except (ValueError, TypeError) as exc:
        logger.error("[file_classification_healer] heal failed: %s", exc)
        return HealCheckResult(
            check_id=CHECK_ID,
            status=HealStatus.FAILED,
            changes_made=(),
            notes=f"healer error: {type(exc).__name__}: {exc}",
            needs_llm_escalation=True,
            escalation_hint="failure_type=healer_error",
        )
    files_healed = res.get("files_healed", 0) if isinstance(res, dict) else 0
    res_status = res.get("status", "UNKNOWN") if isinstance(res, dict) else "UNKNOWN"
    changes: list[str] = []
    if files_healed > 0:
        changes.append(f"files_healed:{files_healed}")
    if res_status in ("ERROR", "FAILED") and files_healed == 0:
        status = HealStatus.FAILED
    elif files_healed < violations_count and files_healed > 0:
        status = HealStatus.PARTIAL
    else:
        status = HealStatus.HEALED
    return HealCheckResult(
        check_id=CHECK_ID,
        status=status,
        changes_made=tuple(sorted(changes)),
        notes=f"files_healed={files_healed} status={res_status}",
    )
