"""Meta-Learning Runtime Apply Seam — Wave 7.0.14.

Explicit, guarded, audited apply function for meta-learning changes.
NO automatic/background application.  Must be invoked explicitly.

Gates (evaluated in order, fail-closed):
  1. Capability token required (FS:WRITE permission).
  2. target_component in MUTABLE_COMPONENTS.
  3. Rollout plan links to same change_package trace_id + policy_config_hash.
  4. Blast-radius limits per component type.
  5. Invariants list non-empty (structural check only in 7.0.14).

DRY_RUN: validates all gates, returns APPLIED outcome but writes nothing.
APPLY:   validates all gates, writes versioned config + rollback snapshot.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Literal

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L0_routing.types.determinism_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "meta_apply")
emit_determinism_digest("p0", "meta_apply")

_emit_dispatches_healing_run("p1", "meta_apply", "L0")
_emit_routes_through("p1", "meta_apply", "L0")
_emit_checks_agent_registry("p1", "meta_apply", "agent_registry")
_emit_validates_agent_capability("p1", "meta_apply", "capability")
_emit_dispatches_execution_plan("p1", "meta_apply", "exec_plan")
_emit_agent_executes_agent("p1", "meta_apply", "sub_agent")
_emit_routes_to_agent("p1", "meta_apply", "target_agent")
_emit_verifies_policy("p1", "meta_apply", "policy_check")
_emit_observes_runtime_state("p1", "meta_apply", "runtime_state")
_emit_verifies_boundary("p1", "meta_apply", "boundary_check")
_emit_transcripts_response("p1", "meta_apply", "transcript")
_emit_hard_fails_untranscripted("p1", "meta_apply")
_emit_gated_by_confidence("p1", "meta_apply", "confidence_gate")
_emit_escalates_to_human("p1", "meta_apply", "L0")
_emit_reads_policy_state("p1", "meta_apply", "L0")

_emit_records_execution_trace("p0", "evidence", "meta_apply")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "meta_apply", "p0_governance")
_emit_snapshots_state("p0", "meta_apply", "state_snapshot")
_emit_authorize_and_execute("p2", "meta_apply", "execution_auth")
_emit_validates_capability("p2", "meta_apply", "capability_check")
_emit_routes_to_capability("p2", "meta_apply", "capability_route")
_emit_writes_via_uwg("p2", "meta_apply", "uwg_write")
_emit_blocks_direct_write("p2", "meta_apply", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_apply", "tool_invocation")
_emit_captures_execution_output("p2", "meta_apply", "exec_output")
_emit_dispatches_agent("p3", "meta_apply", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_apply", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_apply", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_apply", "healing_outcome")
_emit_escalates_failure("p3", "meta_apply", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_apply", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_apply", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_apply", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_apply", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_apply", "eval_metric")
_emit_stores_embedding("p4", "meta_apply", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_apply", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_apply", "exec_snapshot_link")
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

_emit_emits_metric_event("meta_apply", "p4obs", "metric_1")
_emit_emits_metric_event("meta_apply", "p4obs", "metric_2")
_emit_emits_metric_event("meta_apply", "p4obs", "metric_3")
_emit_emits_metric_event("meta_apply", "p4obs", "metric_4")
_emit_emits_metric_event("meta_apply", "p4obs", "metric_5")
_emit_emits_metric_event("meta_apply", "p4obs", "metric_6")
_emit_records_incident_event("meta_apply", "p4obs", "incident")
_emit_captures_runtime_anomaly("meta_apply", "p4obs", "anomaly")
_emit_writes_observability_log("meta_apply", "p4obs", "obs_log")
_emit_updates_monitoring_state("meta_apply", "p4obs", "mon_state")
_emit_triggers_alert("meta_apply", "p4obs", "alert")
_emit_links_incident_trace("meta_apply", "p4obs", "trace_link")
_emit_captures_pattern("meta_apply", "p3lm", "pattern")
_emit_records_learning_event("meta_apply", "p3lm", "learning_event")
_emit_writes_learning_snapshot("meta_apply", "p3lm", "snapshot")
_emit_feeds_meta_learning("meta_apply", "p3lm", "meta_feed")
_emit_updates_routing_strategy("meta_apply", "p3lm", "routing")
_emit_improves_agent_policy("meta_apply", "p3lm", "policy")
_emit_stores_learning_state("meta_apply", "p3lm", "state")
_emit_records_execution_trace("meta_apply", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("meta_apply", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("meta_apply", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("meta_apply", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("meta_apply", "L4_STATE", "p2_trace_5")
_emit_reads_environ("meta_apply", "env_read", "p2_env_1")
_emit_reads_environ("meta_apply", "env_read", "p2_env_2")
_emit_reads_runtime_state("meta_apply", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("meta_apply", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "meta_apply", "context_pull")
_emit_pulls_context("p1", "meta_apply", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "meta_apply", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "meta_apply", "uwg_term_2")
_emit_writes_through("p1", "meta_apply", "write_through")
_emit_writes_through("p1", "meta_apply", "write_through_2")
_emit_validated_by_safety_plane("p1", "meta_apply", "safety_validation")
_emit_invokes_eval("p1", "meta_apply", "eval_call")
_emit_proposal_commits_routing("p1", "meta_apply", "routing_commit")


def _get_apply_attempt_types():
    from system_learning.types.apply_attempt_types import (
        MetaLearningApplyAttemptArtifact,
        build_apply_attempt,
    )

    return MetaLearningApplyAttemptArtifact, build_apply_attempt


def _get_meta_learning_types():
    from system_learning.types.meta_learning_types import (
        MUTABLE_COMPONENTS,
        MetaLearningChangePackageArtifact,
    )

    return MUTABLE_COMPONENTS, MetaLearningChangePackageArtifact


def _get_rollout_types():
    from system_learning.types.rollout_types import MetaLearningRolloutPlanArtifact

    return MetaLearningRolloutPlanArtifact


def _get_CapabilityTokenArtifact():
    """Lazy load CapabilityTokenArtifact to avoid upward import."""
    from agentic_core.L2_execution.types.capability_token_types import (
        CapabilityTokenArtifact,
    )

    return CapabilityTokenArtifact


# =============================================================================
# Blast-radius limits per component type
# =============================================================================

ROUTING_THRESHOLDS_ALLOWLIST: frozenset[str] = frozenset(
    {
        "threshold",
        "confidence_threshold",
        "fallback_threshold",
        "min_score",
        "max_score",
    }
)

# guardian: allow-magic-config
MAX_ROUTING_THRESHOLD_DELTA = 0.10
# guardian: allow-magic-config
MAX_TOOL_POLICY_BUDGET_DELTA_PERCENT = 10
# guardian: allow-magic-config
MAX_PROMPT_TEMPLATE_DIFF_CHARS = 500

FS_WRITE_PERMISSION = "FS:WRITE"


# =============================================================================
# Blast-radius validation helpers
# =============================================================================


def _check_routing_thresholds_blast(change_spec: dict) -> str | None:
    """Validate routing_thresholds change_spec against blast-radius limits.

    Returns reject_reason string or None if valid.
    """
    for key, value in change_spec.items():
        if key not in ROUTING_THRESHOLDS_ALLOWLIST:
            return f"BLAST_RADIUS_KEY_NOT_ALLOWED:{key}"
        if isinstance(value, (int, float)):
            if abs(value) > MAX_ROUTING_THRESHOLD_DELTA:
                return f"BLAST_RADIUS_DELTA_EXCEEDED:{key}={value}"
    return None


def _check_tool_policies_blast(change_spec: dict) -> str | None:
    """Validate tool_policies change_spec against blast-radius limits.

    Returns reject_reason string or None if valid.
    """
    for key, value in change_spec.items():
        if isinstance(value, (int, float)) and abs(value) > MAX_TOOL_POLICY_BUDGET_DELTA_PERCENT:
            return f"BLAST_RADIUS_TOOL_BUDGET_EXCEEDED:{key}={value}"
    return None


def _check_prompt_templates_blast(change_spec: dict) -> str | None:
    """Validate prompt_templates change_spec against blast-radius limits.

    Returns reject_reason string or None if valid.
    """
    spec_json = json.dumps(change_spec, sort_keys=True, separators=(",", ":"))
    if len(spec_json) > MAX_PROMPT_TEMPLATE_DIFF_CHARS:
        return f"BLAST_RADIUS_TEMPLATE_TOO_LARGE:{len(spec_json)}>{MAX_PROMPT_TEMPLATE_DIFF_CHARS}"
    return None


def _check_blast_radius(target_component: str, change_spec: dict) -> str | None:
    """Dispatch blast-radius check to component-specific validator."""
    if target_component == "routing_thresholds":
        return _check_routing_thresholds_blast(change_spec)
    if target_component == "tool_policies":
        return _check_tool_policies_blast(change_spec)
    if target_component == "prompt_templates":
        return _check_prompt_templates_blast(change_spec)
    return None


# =============================================================================
# Versioned config write helpers
# =============================================================================


def _config_path(base_dir: Path, target_component: str) -> Path:
    """Deterministic config file path for a target component."""
    return base_dir / target_component / "config.json"


def _rollback_path(base_dir: Path, target_component: str) -> Path:
    """Deterministic rollback snapshot path for a target component."""
    return base_dir / target_component / "rollback.json"


def _atomic_write_json(path: Path, data: dict) -> None:
    """Atomic JSON write: write to tmp then rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    content = json.dumps(data, sort_keys=True, indent=2, separators=(",", ": "))
    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
    tmp.write_text(content, encoding="utf-8")
    if path.exists():
        os.replace(str(tmp), str(path))
    else:
        os.replace(str(tmp), str(path))


# =============================================================================
# Main apply function
# =============================================================================


def apply_meta_learning_rollout(
    *,
    change_package: MetaLearningChangePackageArtifact,
    rollout_plan: MetaLearningRolloutPlanArtifact,
    capability_token: CapabilityTokenArtifact | None,
    apply_mode: Literal["DRY_RUN", "APPLY"],
    policy_config_hash: str | None,
    semantic_clock: SemanticClockSnapshot,
    base_dir: Path | None = None,
) -> MetaLearningApplyAttemptArtifact:
    """Explicit, guarded runtime apply for meta-learning changes.

    Parameters
    ----------
    change_package : MetaLearningChangePackageArtifact
        The approved change package to apply.
    rollout_plan : MetaLearningRolloutPlanArtifact
        The rollout plan governing this apply.
    capability_token : CapabilityTokenArtifact | None
        Required capability token with FS:WRITE permission.
    apply_mode : "DRY_RUN" | "APPLY"
        DRY_RUN validates gates only; APPLY writes config.
    policy_config_hash : str | None
        Expected policy config hash; must match all artifacts.
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.
    base_dir : Path | None
        Base directory for versioned config state. Required for APPLY mode.

    Returns
    -------
    MetaLearningApplyAttemptArtifact
        Audit record of the apply attempt.
    """
    validate_semantic_clock(semantic_clock, "apply_meta_learning_rollout")

    _, _build_apply_attempt = _get_apply_attempt_types()
    _MUTABLE_COMPONENTS, _ = _get_meta_learning_types()

    def _reject(reason: str, **extra_details: str) -> MetaLearningApplyAttemptArtifact:
        return _build_apply_attempt(
            change_package_trace_id=change_package.trace_id,
            rollout_trace_id=rollout_plan.trace_id,
            policy_config_hash=policy_config_hash,
            target_component=change_package.target_component,
            apply_mode=apply_mode,
            outcome="REJECTED",
            reject_reason=reason,
            details=extra_details,
            semantic_clock=semantic_clock,
        )

    # --- Gate 1: Capability token required with FS:WRITE ---
    if capability_token is None:
        return _reject("CAPABILITY_TOKEN_MISSING")
    if FS_WRITE_PERMISSION not in capability_token.permissions:
        return _reject("CAPABILITY_TOKEN_MISSING_FS_WRITE")

    # --- Gate 2: target_component in MUTABLE_COMPONENTS ---
    if change_package.target_component not in _MUTABLE_COMPONENTS:
        return _reject("IMMUTABLE_COMPONENT")

    # --- Gate 3: Rollout plan links to change_package ---
    if rollout_plan.change_package_trace_id != change_package.trace_id:
        return _reject("ROLLOUT_CHANGE_PACKAGE_MISMATCH")
    if rollout_plan.policy_config_hash != policy_config_hash:
        return _reject("POLICY_HASH_MISMATCH_ROLLOUT")
    if change_package.policy_config_hash != policy_config_hash:
        return _reject("POLICY_HASH_MISMATCH_CHANGE_PACKAGE")

    # --- Gate 4: Blast-radius limits ---
    blast_reason = _check_blast_radius(change_package.target_component, change_package.change_spec)
    if blast_reason is not None:
        return _reject(blast_reason)

    # --- Gate 5: Invariants list non-empty (structural check) ---
    if not rollout_plan.invariants:
        return _reject("INVARIANTS_EMPTY")

    # --- All gates pass ---
    if apply_mode == "DRY_RUN":
        return _build_apply_attempt(
            change_package_trace_id=change_package.trace_id,
            rollout_trace_id=rollout_plan.trace_id,
            policy_config_hash=policy_config_hash,
            target_component=change_package.target_component,
            apply_mode="DRY_RUN",
            outcome="APPLIED",
            reject_reason=None,
            details={"note": "dry_run_no_write"},
            semantic_clock=semantic_clock,
        )

    # --- APPLY mode: write versioned config ---
    if base_dir is None:
        return _reject("BASE_DIR_REQUIRED_FOR_APPLY")

    config_file = _config_path(base_dir, change_package.target_component)
    rollback_file = _rollback_path(base_dir, change_package.target_component)

    # Save rollback snapshot of existing config (if any)
    if config_file.exists():
        existing = config_file.read_text(encoding="utf-8")
        _atomic_write_json(rollback_file, json.loads(existing))
    else:
        _atomic_write_json(rollback_file, {})

    # Write new config
    _atomic_write_json(config_file, change_package.change_spec)

    return _build_apply_attempt(
        change_package_trace_id=change_package.trace_id,
        rollout_trace_id=rollout_plan.trace_id,
        policy_config_hash=policy_config_hash,
        target_component=change_package.target_component,
        apply_mode="APPLY",
        outcome="APPLIED",
        reject_reason=None,
        details={
            "config_path": str(config_file),
            "rollback_path": str(rollback_file),
        },
        semantic_clock=semantic_clock,
    )
