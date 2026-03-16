"""L0 Routing Confidence Monitor — proposal-only min_confidence threshold tuner.

Mirrors the structure of ``l0_threshold_tuner.py`` but targets the
``routing_min_confidence`` surface of AgenticRouter.

When the 10th-percentile routing confidence (``routing_confidence_p10``)
drops below a configurable trigger level, a bounded threshold adjustment is
proposed via ``L0ThresholdChangePackage``.

Design invariants
-----------------
1. Pure function interface — no global mutable state.
2. No wall-clock reads; ``now_utc`` is caller-supplied.
3. All bounds are hard-coded constants; no external config.
4. Proposals are strictly informational — they MUST NOT mutate routing
   or config state directly.
5. Dampening via cooldown + sample-size policies (same validators as
   ``l0_threshold_tuner.py``).
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from system_learning.validators.dampening import (
    CooldownPolicy,
    CooldownViolation,
    SampleSizePolicy,
    SampleSizeViolation,
    assert_cooldown_ok,
    assert_min_sample_size,
)

_emit_records_execution_trace("p0", "evidence", "l0_routing_confidence_monitor")
_emit_applies_guardrail("p0", "l0_routing_confidence_monitor", "p0_governance")
_emit_snapshots_state("p0", "l0_routing_confidence_monitor", "state_snapshot")
emit_replay_key("p0", "l0_routing_confidence_monitor")
emit_determinism_digest("p0", "l0_routing_confidence_monitor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MIN_CONFIDENCE = 0.10
_MAX_CONFIDENCE = 0.80
_MAX_DELTA = 0.05
_DEFAULT_DELTA = 0.03
_P10_TRIGGER = 0.30


# ---------------------------------------------------------------------------
# Change Package
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RoutingConfidenceChangePackage:
    """Immutable, deterministically-hashable routing confidence change proposal.

    Fields
    ------
    surface_name : str
        Always ``"routing_min_confidence"``.
    old_value : float
        Current min_confidence value in AgenticRouter.
    new_value : float
        Proposed min_confidence value.
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
        data = {
            "surface_name": self.surface_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "justification": self.justification,
            "snapshot_id": self.snapshot_id,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Percentile helper
# ---------------------------------------------------------------------------


def _compute_p10(values: list[float]) -> float:
    """Compute the 10th percentile of a sorted list of floats."""
    if not values:
        return 1.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    index = 0.10 * (n - 1)
    lower = int(index)
    upper = min(lower + 1, n - 1)
    fraction = index - lower
    return sorted_vals[lower] + fraction * (sorted_vals[upper] - sorted_vals[lower])


# ---------------------------------------------------------------------------
# Proposal Function
# ---------------------------------------------------------------------------


def propose_routing_confidence_change(
    *,
    snapshot_id: str,
    confidence_values: list[float],
    current_config: dict[str, float],
    now_utc: int,
    history: dict[str, Any],
    cooldown_policy: CooldownPolicy,
    sample_policy: SampleSizePolicy,
) -> RoutingConfidenceChangePackage | None:
    """Propose a routing_min_confidence adjustment when p10 drops below trigger.

    Parameters
    ----------
    snapshot_id : str
        Identifier for the metrics snapshot.
    confidence_values : list[float]
        Recent routing confidence scores (one per routing decision).
    current_config : dict[str, float]
        Must include ``"routing_min_confidence"``.
    now_utc : int
        Current deterministic timestamp.
    history : dict[str, Any]
        Keys: ``"routing_min_confidence_last_update"``,
              ``"routing_min_confidence_n_obs"``.
    cooldown_policy : CooldownPolicy
        Cooldown dampening policy.
    sample_policy : SampleSizePolicy
        Sample-size dampening policy.

    Returns
    -------
    RoutingConfidenceChangePackage | None
        A proposal if adjustment is warranted, ``None`` otherwise.
    """
    surface = "routing_min_confidence"
    current_value = current_config.get(surface)
    if current_value is None or not confidence_values:
        return None

    p10 = round(_compute_p10(confidence_values), 4)

    if p10 >= _P10_TRIGGER:
        return None

    last_update_utc = history.get(f"{surface}_last_update", 0)
    try:
        assert_cooldown_ok(last_update_utc, now_utc, cooldown_policy)
    except CooldownViolation:
        return None

    n_obs = history.get(f"{surface}_n_obs", 0)
    try:
        assert_min_sample_size(n_obs, sample_policy)
    except SampleSizeViolation:
        return None

    new_value = current_value + _DEFAULT_DELTA
    new_value = min(new_value, _MAX_CONFIDENCE)
    new_value = max(new_value, _MIN_CONFIDENCE)
    new_value = round(new_value, 4)

    if new_value == current_value:
        return None

    delta = abs(new_value - current_value)
    if delta > _MAX_DELTA:
        new_value = current_value + (_MAX_DELTA if new_value > current_value else -_MAX_DELTA)
        new_value = round(new_value, 4)

    justification = (
        f"routing_confidence_p10={p10:.4f} below trigger={_P10_TRIGGER}; "
        f"adjusting {surface} from {current_value} to {new_value} (delta={delta:.4f})"
    )
    logger.debug("RoutingConfidenceMonitor: %s", justification)

    return RoutingConfidenceChangePackage(
        surface_name=surface,
        old_value=current_value,
        new_value=new_value,
        justification=justification,
        snapshot_id=snapshot_id,
    )


# ---------------------------------------------------------------------------
# Proposer Adapter (mirrors L0ProposerAdapter pattern)
# ---------------------------------------------------------------------------


class L0RoutingConfidenceProposerAdapter:
    """Adapts ``propose_routing_confidence_change`` to the pipeline proposer protocol.

    The pipeline calls ``proposer.propose(snapshot, confidence_values, config,
    now_utc, history, cooldown, sample)``.
    """

    def propose(
        self,
        snapshot: Any,
        confidence_values: Any,
        config: Any,
        now_utc: int,
        history: Any,
        cooldown: Any,
        sample: Any,
    ) -> RoutingConfidenceChangePackage | None:
        snapshot_id = getattr(snapshot, "snapshot_id", "unknown")

        if not isinstance(confidence_values, list):
            confidence_values = []

        if not isinstance(config, dict):
            config = {}

        if not isinstance(history, dict):
            history = {}

        if cooldown is None:
            # guardian: allow-magic-config
            cooldown = CooldownPolicy(min_seconds_between_updates=3600)

        if sample is None:
            # guardian: allow-magic-config
            sample = SampleSizePolicy(min_observations=10)

        return propose_routing_confidence_change(
            snapshot_id=snapshot_id,
            confidence_values=confidence_values,
            current_config=config,
            now_utc=now_utc,
            history=history,
            cooldown_policy=cooldown,
            sample_policy=sample,
        )


__all__ = [
    "RoutingConfidenceChangePackage",
    "L0RoutingConfidenceProposerAdapter",
    "propose_routing_confidence_change",
]
