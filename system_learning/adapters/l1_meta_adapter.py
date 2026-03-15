"""L1 Meta-Learning Adapter — bridges L1 cognition's local meta-learning to the central pipeline.

L1 has its own ``MetaLearningClient`` (31+ references) and ``MetaLearningAgent``
that use a separate ``MetaLearningProtocol``.  This adapter converts L1-specific
recall/learn outcomes and cache statistics into the central pipeline's telemetry
and audit format so that drift from L1 model changes is captured by the
meta-learning bus.

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class L1TelemetryEvent:
    """A telemetry event extracted from L1 meta-learning data."""

    timestamp_utc: int
    event_type: str
    payload_bytes: bytes


@dataclass(frozen=True, slots=True)
class L1DriftSignal:
    """A drift signal from L1 model calibration changes."""

    surface_name: str
    drift_magnitude: float
    direction: str
    observation_count: int
    snapshot_id: str


class L1MetaAdapter:
    """Bridges L1 MetaLearningClient data into the central pipeline.

    Usage::

        adapter = L1MetaAdapter()
        events = adapter.extract_telemetry(l1_state, now_utc=1234)
        drift = adapter.detect_drift(l1_state, snapshot_id="snap")
    """

    def extract_telemetry(self, l1_state: dict[str, Any], *, now_utc: int) -> list[L1TelemetryEvent]:
        """Extract telemetry events from L1 meta-learning state.

        Parameters
        ----------
        l1_state : dict
            L1-specific state dict, expected to contain keys like
            ``"recall_outcomes"``, ``"learn_outcomes"``, ``"cache_stats"``.
        now_utc : int
            Deterministic timestamp.

        Returns
        -------
        list[L1TelemetryEvent]
            Telemetry events suitable for ingestion into the central
            ``TelemetryStore``.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "L1MetaAdapter.extract_telemetry")

        events: list[L1TelemetryEvent] = []
        for outcome in l1_state.get("recall_outcomes", []):
            if not isinstance(outcome, dict):
                continue
            ts = outcome.get("timestamp_utc", now_utc)
            payload = json.dumps(
                {"source": "l1_recall", "outcome": outcome}, separators=(",", ":"), sort_keys=True
            ).encode("utf-8")
            events.append(
                L1TelemetryEvent(timestamp_utc=ts, event_type="l1_recall_outcome", payload_bytes=payload)
            )
        for outcome in l1_state.get("learn_outcomes", []):
            if not isinstance(outcome, dict):
                continue
            ts = outcome.get("timestamp_utc", now_utc)
            payload = json.dumps(
                {"source": "l1_learn", "outcome": outcome}, separators=(",", ":"), sort_keys=True
            ).encode("utf-8")
            events.append(
                L1TelemetryEvent(timestamp_utc=ts, event_type="l1_learn_outcome", payload_bytes=payload)
            )
        cache_stats = l1_state.get("cache_stats")
        if isinstance(cache_stats, dict):
            payload = json.dumps(
                {"source": "l1_cache", "stats": cache_stats}, separators=(",", ":"), sort_keys=True
            ).encode("utf-8")
            events.append(
                L1TelemetryEvent(timestamp_utc=now_utc, event_type="l1_cache_stats", payload_bytes=payload)
            )
        return events

    def detect_drift(self, l1_state: dict[str, Any], *, snapshot_id: str) -> L1DriftSignal | None:
        """Detect model calibration drift from L1 state.

        Parameters
        ----------
        l1_state : dict
            L1-specific state with ``"confidence_history"`` (list of floats)
            and ``"model_version"``.
        snapshot_id : str
            Pipeline snapshot ID.

        Returns
        -------
        L1DriftSignal | None
            Drift signal if significant drift detected, None otherwise.
        """
        history = l1_state.get("confidence_history", [])
        if not isinstance(history, list) or len(history) < 2:
            return None
        try:
            floats = [float(v) for v in history]
        except (TypeError, ValueError):
            return None
        mid = len(floats) // 2
        if mid == 0:
            return None
        old_mean = sum(floats[:mid]) / mid
        new_mean = sum(floats[mid:]) / (len(floats) - mid)
        drift = new_mean - old_mean
        if abs(drift) < 0.05:
            return None
        return L1DriftSignal(
            surface_name="l1_model_confidence",
            drift_magnitude=round(abs(drift), 4),
            direction="increase" if drift > 0 else "decrease",
            observation_count=len(floats),
            snapshot_id=snapshot_id,
        )


__all__ = ["L1MetaAdapter", "L1TelemetryEvent", "L1DriftSignal"]
