"""G-16-18: L0 threshold tuner — proposal-only optimizer for routing thresholds.

Proposes changes to L0 routing thresholds based on metrics, enforcing:
  - Allowlist constraints (only allowed surfaces)
  - Bounds + max-delta enforcement
  - Cooldown + sample-size dampening
  - Deterministic inputs only (no wall-clock)
  - Proposal-only (no activation)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from system_learning.constraints.delta_enforcer import validate_surface_change
from system_learning.validators.dampening import (
    CooldownPolicy,
    SampleSizePolicy,
    assert_cooldown_ok,
    assert_min_sample_size,
)

# =============================================================================
# ChangePackage (Minimal Implementation for Phase 3)
# =============================================================================


@dataclass(frozen=True, slots=True)
class L0ThresholdChangePackage:
    """Immutable ChangePackage for L0 threshold changes.

    Fields
    ------
    surface_name : str
        The config surface being changed.
    old_value : float
        The current value.
    new_value : float
        The proposed new value.
    justification : str
        Rationale for the change.
    snapshot_id : str
        The snapshot this proposal is based on.
    """

    surface_name: str
    old_value: float
    new_value: float
    justification: str
    snapshot_id: str

    def canonical_bytes(self) -> bytes:
        """Return deterministic canonical byte representation."""
        # Canonical concatenation with delimiter
        parts = [
            self.surface_name.encode("utf-8"),
            str(self.old_value).encode("utf-8"),
            str(self.new_value).encode("utf-8"),
            self.justification.encode("utf-8"),
            self.snapshot_id.encode("utf-8"),
        ]
        return b"\x1f".join(parts)

    def content_hash(self) -> str:
        """Return SHA-256 hash of canonical bytes."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


# =============================================================================
# L0 Threshold Tuner
# =============================================================================


def propose_l0_threshold_changes(
    snapshot_id: str,
    metrics: dict[str, float],
    current_config: dict[str, float],
    now_utc: int,
    history: dict[str, int],
    cooldown_policy: CooldownPolicy,
    sample_policy: SampleSizePolicy,
) -> L0ThresholdChangePackage | None:
    """Propose L0 threshold changes based on metrics.

    Proposal-only: does NOT activate or commit. Returns a ChangePackage
    that can be committed via Phase 2 version store.

    Parameters
    ----------
    snapshot_id : str
        The snapshot this proposal is based on.
    metrics : dict[str, float]
        Observed metrics (e.g., {"escalation_rate": 0.15}).
    current_config : dict[str, float]
        Current L0 threshold values.
    now_utc : int
        Current time (injected, not wall-clock).
    history : dict[str, int]
        Last update timestamps and observation counts per surface.
        Format: {"escalation_threshold_last_update": 1700000000,
                 "escalation_threshold_n_obs": 1500}
    cooldown_policy : CooldownPolicy
        Cooldown policy to enforce.
    sample_policy : SampleSizePolicy
        Sample size policy to enforce.

    Returns
    -------
    L0ThresholdChangePackage | None
        Proposed change, or None if no change needed or dampening violated.

    Raises
    ------
    ConstraintViolation
        If proposed change violates constraints.
    """
    # Example: tune escalation_threshold based on escalation_rate
    surface_name = "escalation_threshold"
    escalation_rate = metrics.get("escalation_rate", 0.0)
    current_value = current_config.get(surface_name, 0.85)

    # Check dampening policies
    last_update = history.get(f"{surface_name}_last_update", 0)
    n_obs = history.get(f"{surface_name}_n_obs", 0)

    try:
        assert_cooldown_ok(last_update, now_utc, cooldown_policy)
        assert_min_sample_size(n_obs, sample_policy)
    except Exception:
        # Dampening violated - no proposal
        return None

    # Simple heuristic: if escalation_rate > 0.20, increase threshold
    # if escalation_rate < 0.10, decrease threshold
    if escalation_rate > 0.20:
        proposed_value = min(current_value + 0.03, 0.95)
    elif escalation_rate < 0.10:
        proposed_value = max(current_value - 0.03, 0.70)
    else:
        # No change needed
        return None

    # Validate constraint
    validate_surface_change(surface_name, current_value, proposed_value)

    # Create proposal
    justification = f"escalation_rate={escalation_rate:.2f}, adjusting threshold"
    return L0ThresholdChangePackage(
        surface_name=surface_name,
        old_value=current_value,
        new_value=proposed_value,
        justification=justification,
        snapshot_id=snapshot_id,
    )
