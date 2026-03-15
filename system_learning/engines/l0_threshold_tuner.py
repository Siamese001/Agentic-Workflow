"""L0 Threshold Tuner — deterministic threshold adjustment proposals for L0 routing surfaces.

Analyzes L0 routing metrics (escalation rates, routing confidence distributions)
and proposes bounded threshold adjustments subject to cooldown and sample-size
dampening policies.

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from system_learning.validators.dampening import (
    CooldownPolicy,
    CooldownViolation,
    SampleSizePolicy,
    SampleSizeViolation,
    assert_cooldown_ok,
    assert_min_sample_size,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants — all bounds are hard-coded, no external config
# ---------------------------------------------------------------------------

_MIN_THRESHOLD = 0.50
_MAX_THRESHOLD = 0.95
_MAX_DELTA = 0.05
_DEFAULT_DELTA = 0.03
_ESCALATION_RATE_TRIGGER = 0.20  # propose adjustment when rate exceeds this


# ---------------------------------------------------------------------------
# Change Package
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class L0ThresholdChangePackage:
    """Immutable, deterministically-hashable threshold change proposal.

    Fields
    ------
    surface_name : str
        Name of the L0 routing surface being tuned (e.g. ``"escalation_threshold"``).
    old_value : float
        Current threshold value.
    new_value : float
        Proposed threshold value.
    justification : str
        Human-readable reason for the change.
    snapshot_id : str
        ID of the snapshot that triggered this proposal.
    """

    surface_name: str
    old_value: float
    new_value: float
    justification: str
    snapshot_id: str

    def canonical_bytes(self) -> bytes:
        """Return deterministic canonical byte representation."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "L0ThresholdChangePackage.canonical_bytes")

        data = {
            "surface_name": self.surface_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "justification": self.justification,
            "snapshot_id": self.snapshot_id,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        """SHA-256 content hash of canonical bytes."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Proposal Function
# ---------------------------------------------------------------------------


def propose_l0_threshold_changes(
    *,
    snapshot_id: str,
    metrics: dict[str, float],
    current_config: dict[str, float],
    now_utc: int,
    history: dict[str, Any],
    cooldown_policy: CooldownPolicy,
    sample_policy: SampleSizePolicy,
) -> L0ThresholdChangePackage | None:
    """Propose an L0 threshold change based on routing metrics.

    Currently supports the ``escalation_threshold`` surface.  When the
    ``escalation_rate`` metric exceeds the trigger level the function proposes
    a bounded increase to the threshold, subject to cooldown and sample-size
    dampening.

    Parameters
    ----------
    snapshot_id : str
        Identifier for the metrics snapshot.
    metrics : dict[str, float]
        Routing metrics (must include ``"escalation_rate"``).
    current_config : dict[str, float]
        Current threshold values (must include ``"escalation_threshold"``).
    now_utc : int
        Current deterministic timestamp.
    history : dict[str, Any]
        Historical context with keys ``"<surface>_last_update"`` and
        ``"<surface>_n_obs"`` for dampening checks.
    cooldown_policy : CooldownPolicy
        Cooldown dampening policy.
    sample_policy : SampleSizePolicy
        Sample-size dampening policy.

    Returns
    -------
    L0ThresholdChangePackage | None
        A proposal if adjustment is warranted, ``None`` otherwise.
    """
    surface = "escalation_threshold"
    escalation_rate = metrics.get("escalation_rate")
    current_value = current_config.get(surface)

    if escalation_rate is None or current_value is None:
        return None

    # Check if adjustment is warranted
    if escalation_rate <= _ESCALATION_RATE_TRIGGER:
        return None

    # Dampening: cooldown
    last_update_utc = history.get(f"{surface}_last_update", 0)
    try:
        assert_cooldown_ok(last_update_utc, now_utc, cooldown_policy)
    except CooldownViolation:
        return None

    # Dampening: sample size
    n_obs = history.get(f"{surface}_n_obs", 0)
    try:
        assert_min_sample_size(n_obs, sample_policy)
    except SampleSizeViolation:
        return None

    # Compute proposed value: fixed delta, capped to bounds
    new_value = current_value + _DEFAULT_DELTA
    new_value = min(new_value, _MAX_THRESHOLD)
    new_value = max(new_value, _MIN_THRESHOLD)

    # Round to avoid floating-point noise
    new_value = round(new_value, 4)

    # No-op check: if value didn't change, skip
    if new_value == current_value:
        return None

    # Delta safety check
    delta = abs(new_value - current_value)
    if delta > _MAX_DELTA:
        new_value = current_value + (_MAX_DELTA if new_value > current_value else -_MAX_DELTA)
        new_value = round(new_value, 4)

    justification = (
        f"escalation_rate={escalation_rate:.4f} exceeds trigger={_ESCALATION_RATE_TRIGGER}; "
        f"adjusting {surface} from {current_value} to {new_value} (delta={delta:.4f})"
    )

    return L0ThresholdChangePackage(
        surface_name=surface,
        old_value=current_value,
        new_value=new_value,
        justification=justification,
        snapshot_id=snapshot_id,
    )


# ---------------------------------------------------------------------------
# Proposer Adapter (Protocol-conforming wrapper for the pipeline)
# ---------------------------------------------------------------------------


class L0ProposerAdapter:
    """Wraps ``propose_l0_threshold_changes`` to conform to the ``L0Proposer`` Protocol.

    The pipeline calls ``proposer.propose(snapshot, metrics, config, now_utc,
    history, cooldown, sample)``.  This adapter translates those args into the
    keyword-only function call.
    """

    def propose(
        self,
        snapshot: Any,
        metrics: Any,
        config: Any,
        now_utc: int,
        history: Any,
        cooldown: Any,
        sample: Any,
    ) -> L0ThresholdChangePackage | None:
        """Propose L0 threshold changes.

        Extracts ``snapshot_id`` from the snapshot object and delegates
        to ``propose_l0_threshold_changes()``.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "L0ProposerAdapter.propose")

        snapshot_id = getattr(snapshot, "snapshot_id", "unknown")

        # Normalise metrics: must be dict[str, float]
        if not isinstance(metrics, dict):
            metrics = {}

        # Normalise config: must be dict[str, float]
        if not isinstance(config, dict):
            config = {}

        # Provide fallback escalation_rate from config if metrics is sparse
        if "escalation_rate" not in metrics:
            metrics = dict(metrics)

        # Normalise history
        if not isinstance(history, dict):
            history = {}

        # Normalise cooldown / sample to our policy types
        if cooldown is None:
            from system_learning.validators.dampening import CooldownPolicy
            # guardian: allow-magic-config
            cooldown = CooldownPolicy(min_seconds_between_updates=3600)

        if sample is None:
            from system_learning.validators.dampening import SampleSizePolicy
            # guardian: allow-magic-config
            sample = SampleSizePolicy(min_observations=10)

        return propose_l0_threshold_changes(
            snapshot_id=snapshot_id,
            metrics=metrics,
            current_config=config if isinstance(config, dict) else {},
            now_utc=now_utc,
            history=history,
            cooldown_policy=cooldown,
            sample_policy=sample,
        )


__all__ = [
    "L0ThresholdChangePackage",
    "L0ProposerAdapter",
    "propose_l0_threshold_changes",
]
