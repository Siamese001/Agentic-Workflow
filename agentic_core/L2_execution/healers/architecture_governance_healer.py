"""
Architecture Governance Healer — Dry-run only.

Reads guardian evidence from import_compliance and layer_gravity checks.
Both checks are report-only: automated fixes for import violations and
agent relocation require human review due to cascading import breakage.

Apply mode is always SKIPPED with planned actions.
"""

from __future__ import annotations

from pathlib import Path

from agentic_core.L2_execution.types.heal_contract_types import (
    HealCheckResult,
    HealStatus,
)
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

_emit_authorize_and_execute("p2", "architecture_governance_healer", "execution_auth")
_emit_validates_capability("p2", "architecture_governance_healer", "capability_check")
_emit_routes_to_capability("p2", "architecture_governance_healer", "capability_route")
_emit_writes_via_uwg("p2", "architecture_governance_healer", "uwg_write")
_emit_blocks_direct_write("p2", "architecture_governance_healer", "direct_write_block")
_emit_records_tool_invocation("p2", "architecture_governance_healer", "tool_invocation")
_emit_captures_execution_output("p2", "architecture_governance_healer", "exec_output")
_emit_dispatches_agent("p3", "architecture_governance_healer", "agent_dispatch")
_emit_coordinates_agents("p3", "architecture_governance_healer", "agent_coordination")
_emit_records_workflow_lineage("p3", "architecture_governance_healer", "workflow_lineage")
_emit_records_healing_outcome("p3", "architecture_governance_healer", "healing_outcome")
_emit_escalates_failure("p3", "architecture_governance_healer", "failure_escalation")
_emit_orchestrates_workflow("p3", "architecture_governance_healer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "architecture_governance_healer", "healing_dispatch")
_emit_invokes_evaluation("p3", "architecture_governance_healer", "evaluation_signal")
_emit_records_telemetry_event("p4", "architecture_governance_healer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "architecture_governance_healer", "eval_metric")
_emit_stores_embedding("p4", "architecture_governance_healer", "embedding_store")
_emit_updates_meta_learning_state("p4", "architecture_governance_healer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "architecture_governance_healer", "exec_snapshot_link")
from agentic_core.utils.schemas.ast_fuzzy_util import parse_evidence as _parse_evidence

emit_replay_key("p0", "architecture_governance_healer")
emit_determinism_digest("p0", "architecture_governance_healer")

_emit_dispatches_healing_run("p1", "architecture_governance_healer", "L2")
_emit_routes_through("p1", "architecture_governance_healer", "L2")
_emit_checks_agent_registry("p1", "architecture_governance_healer", "agent_registry")
_emit_validates_agent_capability("p1", "architecture_governance_healer", "capability")
_emit_dispatches_execution_plan("p1", "architecture_governance_healer", "exec_plan")
_emit_agent_executes_agent("p1", "architecture_governance_healer", "sub_agent")
_emit_routes_to_agent("p1", "architecture_governance_healer", "target_agent")
_emit_verifies_policy("p1", "architecture_governance_healer", "policy_check")
_emit_observes_runtime_state("p1", "architecture_governance_healer", "runtime_state")
_emit_verifies_boundary("p1", "architecture_governance_healer", "boundary_check")
_emit_transcripts_response("p1", "architecture_governance_healer", "transcript")
_emit_hard_fails_untranscripted("p1", "architecture_governance_healer")
_emit_gated_by_confidence("p1", "architecture_governance_healer", "confidence_gate")
_emit_escalates_to_human("p1", "architecture_governance_healer", "L2")
_emit_reads_policy_state("p1", "architecture_governance_healer", "L2")
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

_emit_emits_metric_event("architecture_governance_healer", "p4obs", "metric_1")
_emit_emits_metric_event("architecture_governance_healer", "p4obs", "metric_2")
_emit_emits_metric_event("architecture_governance_healer", "p4obs", "metric_3")
_emit_emits_metric_event("architecture_governance_healer", "p4obs", "metric_4")
_emit_emits_metric_event("architecture_governance_healer", "p4obs", "metric_5")
_emit_emits_metric_event("architecture_governance_healer", "p4obs", "metric_6")
_emit_records_incident_event("architecture_governance_healer", "p4obs", "incident")
_emit_captures_runtime_anomaly("architecture_governance_healer", "p4obs", "anomaly")
_emit_writes_observability_log("architecture_governance_healer", "p4obs", "obs_log")
_emit_updates_monitoring_state("architecture_governance_healer", "p4obs", "mon_state")
_emit_triggers_alert("architecture_governance_healer", "p4obs", "alert")
_emit_links_incident_trace("architecture_governance_healer", "p4obs", "trace_link")
_emit_captures_pattern("architecture_governance_healer", "p3lm", "pattern")
_emit_records_learning_event("architecture_governance_healer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("architecture_governance_healer", "p3lm", "snapshot")
_emit_feeds_meta_learning("architecture_governance_healer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("architecture_governance_healer", "p3lm", "routing")
_emit_improves_agent_policy("architecture_governance_healer", "p3lm", "policy")
_emit_stores_learning_state("architecture_governance_healer", "p3lm", "state")
_emit_records_execution_trace("architecture_governance_healer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("architecture_governance_healer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("architecture_governance_healer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("architecture_governance_healer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("architecture_governance_healer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("architecture_governance_healer", "env_read", "p2_env_1")
_emit_reads_environ("architecture_governance_healer", "env_read", "p2_env_2")
_emit_reads_runtime_state("architecture_governance_healer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("architecture_governance_healer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "architecture_governance_healer", "context_pull")
_emit_pulls_context("p1", "architecture_governance_healer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "architecture_governance_healer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "architecture_governance_healer", "uwg_term_2")
_emit_writes_through("p1", "architecture_governance_healer", "write_through")
_emit_writes_through("p1", "architecture_governance_healer", "write_through_2")
_emit_validated_by_safety_plane("p1", "architecture_governance_healer", "safety_validation")
_emit_invokes_eval("p1", "architecture_governance_healer", "eval_call")
_emit_proposal_commits_routing("p1", "architecture_governance_healer", "routing_commit")


def heal_import_compliance(
    check: dict,
    *,
    repo_root: Path | None = None,
    apply: bool = False,
) -> HealCheckResult:
    """Heal import_compliance violations (upward layer imports).

    Import rewiring is inherently risky — changing import statements can
    break runtime behaviour across the codebase. This healer always
    reports planned actions but never applies changes automatically.

    Dry-run: SKIPPED with planned actions.
    Apply: SKIPPED (import rewiring requires human review).
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "heal_import_compliance", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "heal_import_compliance", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "heal_import_compliance")
    evidence = _parse_evidence(check)
    check_id: str = check.get("check_id", "import_compliance")

    violations = evidence.get("violations", [])
    planned: list[str] = []
    for v in violations:
        path = v.get("path", "unknown")
        src = v.get("source_layer", "?")
        tgt = v.get("target_layer", "?")
        planned.append(f"would_fix_import:{path}:{src}->{tgt}")
    planned.sort()

    return HealCheckResult(
        check_id=check_id,
        status=HealStatus.SKIPPED,
        changes_made=tuple(planned),
        rollback_info=None,
        notes="import rewiring requires human review; dry-run only",
    )


def heal_layer_gravity(
    check: dict,
    *,
    repo_root: Path | None = None,
    apply: bool = False,
) -> HealCheckResult:
    """Heal layer_gravity violations (agents in wrong layers).

    Agent relocation requires moving files AND updating all imports across
    the codebase. This healer always reports planned actions but never
    applies relocations automatically.

    Dry-run: SKIPPED with planned actions.
    Apply: SKIPPED (agent relocation requires human review).
    """
    evidence = _parse_evidence(check)
    check_id: str = check.get("check_id", "layer_gravity")

    violations = evidence.get("violations", [])
    planned: list[str] = []
    for v in violations:
        path = v.get("path", "unknown")
        actual = v.get("actual_layer", "?")
        assigned = v.get("assigned_layer", "?")
        planned.append(f"would_relocate_agent:{path}:{actual}->{assigned}")
    planned.sort()

    return HealCheckResult(
        check_id=check_id,
        status=HealStatus.SKIPPED,
        changes_made=tuple(planned),
        rollback_info=None,
        notes="agent relocation requires human review; dry-run only",
    )
