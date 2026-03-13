"""L1 Model Proposer — proposes model calibration adjustments for L1 cognition.

Analyzes L1 model confidence distributions and drift signals to propose
bounded calibration adjustments (temperature, top_p, etc.).

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)
_CONFIDENCE_DRIFT_THRESHOLD = 0.15
_MIN_OBSERVATIONS = 5
_TEMPERATURE_DELTA = 0.05
_TEMPERATURE_MIN = 0.0
_TEMPERATURE_MAX = 2.0


@dataclass(frozen=True, slots=True)
class L1ModelChangePackage:
    """Immutable model calibration adjustment proposal."""

    surface_name: str
    parameter: str
    old_value: float
    new_value: float
    justification: str
    snapshot_id: str

    def canonical_bytes(self) -> bytes:
        data = {
            "surface_name": self.surface_name,
            "parameter": self.parameter,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "justification": self.justification,
            "snapshot_id": self.snapshot_id,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


class L1ModelProposer:
    """Concrete L1 proposer conforming to the L1Proposer Protocol."""

    def propose(
        self, snapshot: Any, metrics: Any, config: Any, now_utc: int, history: Any, cooldown: Any, sample: Any
    ) -> L1ModelChangePackage | None:
        """Propose L1 model calibration changes.

        Parameters
        ----------
        metrics : dict
            Must contain ``"l1_confidence_drift"`` and
            ``"l1_observation_count"``.
        config : dict
            Current L1 config with ``"temperature"``.
        """
        if not isinstance(metrics, dict) or not isinstance(config, dict):
            return None
        confidence_drift = metrics.get("l1_confidence_drift", 0.0)
        n_obs = metrics.get("l1_observation_count", 0)
        if n_obs < _MIN_OBSERVATIONS:
            return None
        if abs(confidence_drift) <= _CONFIDENCE_DRIFT_THRESHOLD:
            return None
        snapshot_id = getattr(snapshot, "snapshot_id", "unknown")
        current_temp = config.get("temperature", 0.7)
        if confidence_drift > 0:
            new_temp = min(current_temp + _TEMPERATURE_DELTA, _TEMPERATURE_MAX)
            direction = "increase"
        else:
            new_temp = max(current_temp - _TEMPERATURE_DELTA, _TEMPERATURE_MIN)
            direction = "decrease"
        new_temp = round(new_temp, 4)
        if new_temp == current_temp:
            return None
        return L1ModelChangePackage(
            surface_name="l1_model_temperature",
            parameter="temperature",
            old_value=current_temp,
            new_value=new_temp,
            justification=f"L1 confidence drift {confidence_drift:.3f} exceeds threshold {_CONFIDENCE_DRIFT_THRESHOLD}; {direction} temperature from {current_temp} to {new_temp}",
            snapshot_id=snapshot_id,
        )


__all__ = ["L1ModelProposer", "L1ModelChangePackage"]
