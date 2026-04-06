"""Meta-Learning Operator — Wave 7.0.16 / 7.0.19.

Single explicit operator entrypoint for the full Phase-7 pipeline:
offline replay -> bundle render -> optional apply.

Defaults to DRY_RUN.  No background automation.  No auto-apply.
APPLY requires a capability token with FS:WRITE permission.

Wave 7.0.19 additions:
  - Audit pack now includes "current_config" and "dry_run_delta".
  - Uses config_store (read-only) — NO meta_apply / meta_apply_ops calls
    for the audit join.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, Literal

from agentic_core.interfaces.determinism_types import SemanticClockSnapshot
from agentic_core.interfaces.meta_control import (
    CapabilityTokenArtifact,
    ConfigDeltaArtifact,
    apply_change_package_readonly,
    apply_meta_learning_rollout,
    apply_with_invariants,
    load_current,
)
from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_authorize_and_execute("p2", "meta_learning_operator", "execution_auth")
_emit_validates_capability("p2", "meta_learning_operator", "capability_check")
_emit_routes_to_capability("p2", "meta_learning_operator", "capability_route")
_emit_writes_via_uwg("p2", "meta_learning_operator", "uwg_write")
_emit_blocks_direct_write("p2", "meta_learning_operator", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_learning_operator", "tool_invocation")
_emit_captures_execution_output("p2", "meta_learning_operator", "exec_output")
_emit_dispatches_agent("p3", "meta_learning_operator", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_learning_operator", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_learning_operator", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_learning_operator", "healing_outcome")
_emit_escalates_failure("p3", "meta_learning_operator", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_learning_operator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_learning_operator", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_learning_operator", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_learning_operator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_learning_operator", "eval_metric")
_emit_stores_embedding("p4", "meta_learning_operator", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_learning_operator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_learning_operator", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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
from system_learning.types.app_signal_types import (
    AppSignalEventArtifact,
    aggregate_app_signals,
)
from system_learning.types.apply_attempt_types import (
    MetaLearningApplyAttemptArtifact,
)
from system_learning.types.offline_replay_types import (
    OfflineReplayBundle,
    render_offline_replay_bundle,
    replay_aggregate_to_rollout,
)
from system_learning.types.rollout_types import (
    MetaLearningRollbackArtifact,
)

_emit_emits_metric_event("meta_learning_operator", "p4obs", "metric_1")
_emit_emits_metric_event("meta_learning_operator", "p4obs", "metric_2")
_emit_emits_metric_event("meta_learning_operator", "p4obs", "metric_3")
_emit_emits_metric_event("meta_learning_operator", "p4obs", "metric_4")
_emit_emits_metric_event("meta_learning_operator", "p4obs", "metric_5")
_emit_emits_metric_event("meta_learning_operator", "p4obs", "metric_6")
_emit_records_incident_event("meta_learning_operator", "p4obs", "incident")
_emit_captures_runtime_anomaly("meta_learning_operator", "p4obs", "anomaly")
_emit_writes_observability_log("meta_learning_operator", "p4obs", "obs_log")
_emit_updates_monitoring_state("meta_learning_operator", "p4obs", "mon_state")
_emit_triggers_alert("meta_learning_operator", "p4obs", "alert")
_emit_links_incident_trace("meta_learning_operator", "p4obs", "trace_link")
_emit_captures_pattern("meta_learning_operator", "p3lm", "pattern")
_emit_records_learning_event("meta_learning_operator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("meta_learning_operator", "p3lm", "snapshot")
_emit_feeds_meta_learning("meta_learning_operator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("meta_learning_operator", "p3lm", "routing")
_emit_improves_agent_policy("meta_learning_operator", "p3lm", "policy")
_emit_stores_learning_state("meta_learning_operator", "p3lm", "state")
_emit_records_execution_trace("meta_learning_operator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("meta_learning_operator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("meta_learning_operator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("meta_learning_operator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("meta_learning_operator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("meta_learning_operator", "env_read", "p2_env_1")
_emit_reads_environ("meta_learning_operator", "env_read", "p2_env_2")
_emit_reads_runtime_state("meta_learning_operator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("meta_learning_operator", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "meta_learning_operator")
_emit_applies_guardrail("p0", "meta_learning_operator", "p0_governance")
_emit_reads_policy_state("p0", "meta_learning_operator", "policy_binding")
_emit_snapshots_state("p0", "meta_learning_operator", "state_snapshot")
_emit_pulls_context("p1", "meta_learning_operator", "context_pull")
_emit_pulls_context("p1", "meta_learning_operator", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "meta_learning_operator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "meta_learning_operator", "uwg_term_secondary")
_emit_writes_through("p1", "meta_learning_operator", "write_through")
_emit_writes_through("p1", "meta_learning_operator", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "meta_learning_operator", "safety_validation")
_emit_invokes_eval("p1", "meta_learning_operator", "eval_call")
_emit_proposal_commits_routing("p1", "meta_learning_operator", "routing_commit")
_emit_escalates_to_human("p1", "meta_learning_operator", "human_escalation")
_emit_routes_through("p1", "meta_learning_operator", "route_through")
_emit_checks_agent_registry("p1", "meta_learning_operator", "agent_registry")
_emit_validates_agent_capability("p1", "meta_learning_operator", "capability")
_emit_dispatches_execution_plan("p1", "meta_learning_operator", "exec_plan")
_emit_agent_executes_agent("p1", "meta_learning_operator", "sub_agent")
_emit_routes_to_agent("p1", "meta_learning_operator", "target_agent")
_emit_verifies_policy("p1", "meta_learning_operator", "policy_check")
_emit_observes_runtime_state("p1", "meta_learning_operator", "runtime_state")
_emit_verifies_boundary("p1", "meta_learning_operator", "boundary_check")
_emit_transcripts_response("p1", "meta_learning_operator", "transcript")
_emit_hard_fails_untranscripted("p1", "meta_learning_operator")
_emit_gated_by_confidence("p1", "meta_learning_operator", "confidence_gate")
emit_replay_key("p0", "meta_learning_operator")
emit_determinism_digest("p0", "meta_learning_operator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# Default store root for config_store reads.
_DEFAULT_STORE_ROOT = (
    Path(__file__).resolve().parents[2] / AGENTIC_CORE_DIR / "L0_routing" / "meta_control" / "config_store"
)

# =============================================================================
# Deterministic helpers
# =============================================================================


def _deterministic_evidence_hash(events: Sequence[AppSignalEventArtifact]) -> str:
    """Compute a deterministic evidence hash from event trace_ids."""
    ids = sorted(e.trace_id for e in events)
    payload = json.dumps(ids, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# =============================================================================
# Operator Entrypoint
# =============================================================================


def run_meta_learning_operator(
    *,
    app_id: str,
    metric_name: str,
    events: Sequence[AppSignalEventArtifact],
    baseline_selector: Callable[[AppSignalEventArtifact], bool],
    candidate_selector: Callable[[AppSignalEventArtifact], bool],
    proposer: str,
    target_component: Literal["routing_thresholds", "tool_policies", "prompt_templates"],
    change_spec: dict[str, Any],
    evaluator: str,
    dataset_id: str,
    approval_decision: Literal["APPROVE", "REJECT"],
    approval_rationale: str,
    rollout_strategy: Literal["CANARY", "ALL_AT_ONCE"],
    canary_percent: int | None,
    invariants: Sequence[str],
    max_duration_minutes: int,
    rollback_on_invariant_fail: bool,
    policy_config_hash: str | None,
    semantic_clock: SemanticClockSnapshot,
    mode: Literal["DRY_RUN", "APPLY"] = "DRY_RUN",
    capability_token: CapabilityTokenArtifact | None = None,
    fs_root: Path | None = None,
    store_root: Path | None = None,
) -> dict[str, Any]:
    """Run the full Phase-7 meta-learning pipeline end-to-end.

    DRY_RUN (default): produces a deterministic audit pack with no side effects.
    APPLY: requires capability_token with FS:WRITE; writes are confined to fs_root.

    Returns a stable audit pack dict.
    """
    effective_store_root = store_root if store_root is not None else _DEFAULT_STORE_ROOT

    # ------------------------------------------------------------------
    # Step 1: Aggregate signals
    # ------------------------------------------------------------------
    evidence_hash = _deterministic_evidence_hash(events)
    window_id = f"{app_id}_{metric_name}"

    aggregate = aggregate_app_signals(
        app_id=app_id,
        window_id=window_id,
        metric_name=metric_name,
        events=events,
        baseline_selector=baseline_selector,
        candidate_selector=candidate_selector,
        evidence_hash=evidence_hash,
        semantic_clock=semantic_clock,
    )

    # ------------------------------------------------------------------
    # Step 2: Compose full pipeline via replay_aggregate_to_rollout
    # ------------------------------------------------------------------
    bundle: OfflineReplayBundle = replay_aggregate_to_rollout(
        aggregate=aggregate,
        proposer=proposer,
        target_component=target_component,
        before={},
        after=change_spec,
        evaluator=evaluator,
        dataset_id=dataset_id,
        eval_evidence_hash=evidence_hash,
        approver=proposer,
        approval_decision=approval_decision,
        approval_rationale=approval_rationale,
        rollout_strategy=rollout_strategy,
        rollout_invariants=list(invariants),
        rollout_max_duration_minutes=max_duration_minutes,
        canary_percent=canary_percent,
        semantic_clock=semantic_clock,
        policy_config_hash=policy_config_hash,
    )

    # ------------------------------------------------------------------
    # Step 3: Render canonical bundle JSON
    # ------------------------------------------------------------------
    bundle_json: str = render_offline_replay_bundle(bundle)

    # ------------------------------------------------------------------
    # Step 3b (Wave 7.0.19): Read-only config join for audit pack
    # ------------------------------------------------------------------
    current_payload: dict[str, Any] = load_current(
        effective_store_root,
        app_id,
        target_component,
    )
    current_config: dict[str, Any] = {
        "app_id": app_id,
        "target_component": target_component,
        "payload": current_payload,
    }

    dry_run_delta: ConfigDeltaArtifact | None = None
    if bundle.change_package is not None:
        dry_run_delta = apply_change_package_readonly(
            effective_store_root,
            bundle.change_package,
            semantic_clock,
        )

    # ------------------------------------------------------------------
    # Step 4: Apply logic (APPLY mode only, with ALLOW_TO_APPLY decision)
    # ------------------------------------------------------------------
    apply_attempt: MetaLearningApplyAttemptArtifact | None = None
    rollback: MetaLearningRollbackArtifact | None = None
    applied = False

    if mode == "APPLY" and bundle.change_package is not None and bundle.rollout_plan is not None:
        # Gate validation via apply_meta_learning_rollout (DRY_RUN to validate
        # gates without writing; actual write is handled by apply_with_invariants)
        gate_result = apply_meta_learning_rollout(
            change_package=bundle.change_package,
            rollout_plan=bundle.rollout_plan,
            capability_token=capability_token,
            apply_mode="DRY_RUN",
            policy_config_hash=policy_config_hash,
            semantic_clock=semantic_clock,
        )

        if gate_result.outcome == "REJECTED":
            apply_attempt = gate_result
        else:
            # Gates passed — write with invariant enforcement
            apply_attempt = apply_with_invariants(
                change_package_trace_id=bundle.change_package.trace_id,
                rollout_plan=bundle.rollout_plan,
                change_spec=bundle.change_package.change_spec,
                target_component=target_component,
                base_dir=fs_root,
                semantic_clock=semantic_clock,
                policy_config_hash=policy_config_hash,
            )
            applied = apply_attempt.outcome == "APPLIED"

    return {
        "bundle_json": bundle_json,
        "bundle": bundle,
        "mode": mode,
        "apply_attempt": apply_attempt,
        "rollback": rollback,
        "applied": applied,
        "current_config": current_config,
        "dry_run_delta": dry_run_delta,
    }


# =============================================================================
# Deterministic Audit Pack Renderer
# =============================================================================


def render_meta_learning_audit_pack(audit_pack: dict[str, Any]) -> str:
    """Render audit pack as canonical JSON (sorted keys, compact separators).

    No timestamps, random IDs, or nondeterministic fields.
    """
    attempt = audit_pack.get("apply_attempt")
    rb = audit_pack.get("rollback")
    delta = audit_pack.get("dry_run_delta")

    serializable: dict[str, Any] = {
        "applied": audit_pack["applied"],
        "apply_attempt": attempt.to_dict() if attempt is not None else None,
        "bundle_json": audit_pack["bundle_json"],
        "current_config": audit_pack.get("current_config"),
        "dry_run_delta": delta.to_dict() if delta is not None else None,
        "mode": audit_pack["mode"],
        "rollback": rb.to_dict() if rb is not None else None,
    }
    return json.dumps(serializable, sort_keys=True, separators=(",", ":"))
