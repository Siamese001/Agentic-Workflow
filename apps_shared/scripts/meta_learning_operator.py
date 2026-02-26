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

# Default store root for config_store reads.
_DEFAULT_STORE_ROOT = (
    Path(__file__).resolve().parents[2] / "agentic_core" / "L0_routing" / "meta_control" / "config_store"
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
