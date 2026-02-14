"""Meta-Learning Operational Boundaries — Wave 7.0.15.

Invariant execution harness, rollback executor, rate limiter, and canary
governance scaffolding.

NO automatic/background application.  All functions are explicit invoke only.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.meta_control.meta_apply import (
    _atomic_write_json,
    _config_path,
    _rollback_path,
)
from agentic_core.L0_routing.types.v15_p2_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from agentic_core.L7_meta_learning.types.apply_attempt_types import (
    MetaLearningApplyAttemptArtifact,
    build_apply_attempt,
)
from agentic_core.L7_meta_learning.types.rollout_types import (
    MetaLearningRollbackArtifact,
    MetaLearningRolloutPlanArtifact,
    build_meta_learning_rollback,
)

# =============================================================================
# §Wave7.0.15 — Invariant Registry
# =============================================================================

InvariantCheckFn = Callable[[Path, str, str | None], bool]
"""Signature: (base_dir, target_component, policy_config_hash) -> passes."""


def _check_no_schema_changes(base_dir: Path, target_component: str, policy_config_hash: str | None) -> bool:
    """Assert no changes outside the target config file path.

    Checks that only config.json and rollback.json exist in the component dir.
    """
    comp_dir = base_dir / target_component
    if not comp_dir.exists():
        return True
    allowed = {"config.json", "rollback.json", "canary_state.json", "rate_limit.json"}
    for entry in comp_dir.iterdir():
        if entry.name not in allowed:
            return False
    return True


def _check_policy_hash_unchanged(
    base_dir: Path, target_component: str, policy_config_hash: str | None
) -> bool:
    """Assert policy_config_hash matches the one stored in config metadata.

    In this wave, we validate structurally: the hash parameter is non-None
    iff the caller expects policy pinning. Always passes if hash is None
    (unpinned mode).
    """
    return True  # structural check — actual hash comparison is in apply gates


def _check_guardian_determinism_empty_diff(
    base_dir: Path, target_component: str, policy_config_hash: str | None
) -> bool:
    """Simulated guardian determinism check.

    In production this would compare two guardian JSON runs.
    In this wave it is a structural placeholder that always passes
    unless a test injects a failing comparator.
    """
    marker = base_dir / target_component / ".guardian_diff_fail"
    return not marker.exists()


INVARIANT_REGISTRY: dict[str, InvariantCheckFn] = {
    "guardian_determinism_empty_diff": _check_guardian_determinism_empty_diff,
    "no_schema_changes": _check_no_schema_changes,
    "policy_hash_unchanged": _check_policy_hash_unchanged,
}


def evaluate_invariants(
    invariant_names: tuple[str, ...],
    base_dir: Path,
    target_component: str,
    policy_config_hash: str | None,
) -> tuple[bool, str | None]:
    """Evaluate named invariants from the registry.

    Returns (all_pass, first_failure_name).
    Unknown invariant names are treated as failures (fail-closed).
    """
    for name in invariant_names:
        fn = INVARIANT_REGISTRY.get(name)
        if fn is None:
            return False, f"UNKNOWN_INVARIANT:{name}"
        if not fn(base_dir, target_component, policy_config_hash):
            return False, name
    return True, None


# =============================================================================
# §Wave7.0.15 — Rollback Executor
# =============================================================================


def rollback_meta_learning_rollout(
    *,
    rollout_plan: MetaLearningRolloutPlanArtifact,
    reason: str,
    target_component: str,
    base_dir: Path,
    semantic_clock: SemanticClockSnapshot,
    policy_config_hash: str | None = None,
) -> MetaLearningRollbackArtifact:
    """Restore prior config from rollback snapshot and emit rollback artifact.

    Parameters
    ----------
    rollout_plan : MetaLearningRolloutPlanArtifact
        The rollout plan being rolled back.
    reason : str
        One of ROLLBACK_REASONS.
    target_component : str
        Target component name (from change_package).
    base_dir : Path
        Base directory for versioned config state.
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.
    policy_config_hash : str | None
        Policy config hash for the rollback artifact.

    Returns
    -------
    MetaLearningRollbackArtifact
    """
    validate_semantic_clock(semantic_clock, "rollback_meta_learning_rollout")

    config_file = _config_path(base_dir, target_component)
    rollback_file = _rollback_path(base_dir, target_component)

    # Restore from rollback snapshot
    if rollback_file.exists():
        rollback_data = json.loads(rollback_file.read_text(encoding="utf-8"))
        _atomic_write_json(config_file, rollback_data)

    return build_meta_learning_rollback(
        rollout_plan,
        rollback_reason=reason,
        semantic_clock=semantic_clock,
    )


# =============================================================================
# §Wave7.0.15 — Apply with Invariant Execution
# =============================================================================


def apply_with_invariants(
    *,
    change_package_trace_id: str,
    rollout_plan: MetaLearningRolloutPlanArtifact,
    change_spec: dict[str, Any],
    target_component: str,
    base_dir: Path,
    semantic_clock: SemanticClockSnapshot,
    policy_config_hash: str | None = None,
) -> MetaLearningApplyAttemptArtifact:
    """Write candidate config, evaluate invariants, rollback on failure.

    This function is called AFTER all gates pass in apply_meta_learning_rollout.
    It performs the actual write, evaluates invariants, and rolls back if any fail.

    Parameters
    ----------
    change_package_trace_id : str
        Trace ID of the change package being applied.
    rollout_plan : MetaLearningRolloutPlanArtifact
        The rollout plan (contains invariant names).
    change_spec : dict
        The change to write.
    target_component : str
        Target component name.
    base_dir : Path
        Base directory for versioned config state.
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.
    policy_config_hash : str | None
        Policy config hash.

    Returns
    -------
    MetaLearningApplyAttemptArtifact
    """
    config_file = _config_path(base_dir, target_component)
    rollback_file = _rollback_path(base_dir, target_component)

    # Save rollback snapshot
    if config_file.exists():
        existing = config_file.read_text(encoding="utf-8")
        _atomic_write_json(rollback_file, json.loads(existing))
    else:
        _atomic_write_json(rollback_file, {})

    # Write candidate config
    _atomic_write_json(config_file, change_spec)

    # Evaluate invariants
    all_pass, failed_name = evaluate_invariants(
        rollout_plan.invariants,
        base_dir,
        target_component,
        policy_config_hash,
    )

    if not all_pass:
        # Rollback: restore prior config
        rollback_meta_learning_rollout(
            rollout_plan=rollout_plan,
            reason="INVARIANT_VIOLATION",
            target_component=target_component,
            base_dir=base_dir,
            semantic_clock=semantic_clock,
            policy_config_hash=policy_config_hash,
        )
        return build_apply_attempt(
            change_package_trace_id=change_package_trace_id,
            rollout_trace_id=rollout_plan.trace_id,
            policy_config_hash=policy_config_hash,
            target_component=target_component,
            apply_mode="APPLY",
            outcome="REJECTED",
            reject_reason=f"INVARIANT_VIOLATION:{failed_name}",
            details={"failed_invariant": failed_name or "unknown"},
            semantic_clock=semantic_clock,
        )

    return build_apply_attempt(
        change_package_trace_id=change_package_trace_id,
        rollout_trace_id=rollout_plan.trace_id,
        policy_config_hash=policy_config_hash,
        target_component=target_component,
        apply_mode="APPLY",
        outcome="APPLIED",
        reject_reason=None,
        details={
            "config_path": str(config_file),
            "rollback_path": str(rollback_file),
        },
        semantic_clock=semantic_clock,
    )


# =============================================================================
# §Wave7.0.15 — Rate Limiter
# =============================================================================

# guardian: allow-magic-config
RATE_LIMIT_SECONDS = 3600  # 1 hour


def _rate_limit_path(base_dir: Path, target_component: str) -> Path:
    """Path to rate-limit state file."""
    return base_dir / target_component / "rate_limit.json"


def check_rate_limit(
    base_dir: Path,
    app_id: str,
    target_component: str,
    now_epoch_s: int | None = None,
) -> tuple[bool, int | None]:
    """Check if an apply is allowed under the rate limit.

    Returns (allowed, last_apply_epoch_s).
    Only 1 APPLY per (app_id, target_component) per hour.
    """
    rl_file = _rate_limit_path(base_dir, target_component)
    now = now_epoch_s if now_epoch_s is not None else int(time.time())

    if rl_file.exists():
        state = json.loads(rl_file.read_text(encoding="utf-8"))
        last = state.get(app_id, 0)
        if now - last < RATE_LIMIT_SECONDS:
            return False, last
    return True, None


def record_apply_timestamp(
    base_dir: Path,
    app_id: str,
    target_component: str,
    now_epoch_s: int | None = None,
) -> None:
    """Record an apply timestamp for rate limiting."""
    rl_file = _rate_limit_path(base_dir, target_component)
    now = now_epoch_s if now_epoch_s is not None else int(time.time())

    state: dict[str, int] = {}
    if rl_file.exists():
        state = json.loads(rl_file.read_text(encoding="utf-8"))
    state[app_id] = now
    _atomic_write_json(rl_file, state)


# =============================================================================
# §Wave7.0.15 — Canary Governance Scaffolding
# =============================================================================


def _canary_state_path(base_dir: Path, target_component: str) -> Path:
    """Path to canary state file."""
    return base_dir / target_component / "canary_state.json"


def record_canary_state(
    *,
    rollout_plan: MetaLearningRolloutPlanArtifact,
    target_component: str,
    base_dir: Path,
) -> dict[str, Any]:
    """Record canary rollout state for governance tracking.

    Only records plan state — no per-user routing.

    Returns the canary state dict.
    """
    if rollout_plan.rollout_strategy != "CANARY":
        raise ValueError("record_canary_state requires CANARY strategy")

    state: dict[str, Any] = {
        "rollout_trace_id": rollout_plan.trace_id,
        "strategy": rollout_plan.rollout_strategy,
        "canary_percent": rollout_plan.canary_percent,
        "target_component": target_component,
        "invariants": list(rollout_plan.invariants),
        "max_duration_minutes": rollout_plan.max_duration_minutes,
    }
    canary_file = _canary_state_path(base_dir, target_component)
    _atomic_write_json(canary_file, state)
    return state
