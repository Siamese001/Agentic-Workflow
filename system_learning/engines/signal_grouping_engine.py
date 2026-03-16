"""Signal Grouping Engine — clusters similar detection signals for the meta-learning bus.

Groups L6 detection signals by type and component, producing clustered
summaries that the pipeline uses for pattern analysis and drift monitoring.

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "signal_grouping_engine", "p0_governance")
_emit_reads_policy_state("p0", "signal_grouping_engine", "policy_binding")
_emit_snapshots_state("p0", "signal_grouping_engine", "state_snapshot")
emit_replay_key("p0", "signal_grouping_engine")
emit_determinism_digest("p0", "signal_grouping_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SignalGroup:
    """A cluster of similar detection signals."""

    group_key: str
    signal_type: str
    component: str
    count: int
    earliest_utc: int
    latest_utc: int
    sample_payloads: tuple[bytes, ...]

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SignalGroup.canonical_bytes")

        data = {
            "group_key": self.group_key,
            "signal_type": self.signal_type,
            "component": self.component,
            "count": self.count,
            "earliest_utc": self.earliest_utc,
            "latest_utc": self.latest_utc,
            "sample_count": len(self.sample_payloads),
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class SignalGroupingReport:
    """Report of grouped detection signals."""

    snapshot_id: str
    groups: tuple[SignalGroup, ...]
    total_signals: int
    total_groups: int

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SignalGroupingReport.canonical_bytes")

        data = {
            "snapshot_id": self.snapshot_id,
            "total_signals": self.total_signals,
            "total_groups": self.total_groups,
            "groups": [json.loads(g.canonical_bytes().decode("utf-8")) for g in self.groups],
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


_MAX_SAMPLE_PAYLOADS = 3


class SignalGroupingEngine:
    """Groups detection signals by (signal_type, component) pairs.

    Parameters
    ----------
    max_samples : int
        Maximum number of sample payloads to keep per group.
    """

    def __init__(self, max_samples: int = _MAX_SAMPLE_PAYLOADS) -> None:
        self._max_samples = max_samples

    def group_signals(self, *, snapshot_id: str, signals: list[dict[str, Any]]) -> SignalGroupingReport:
        """Group detection signals by type and component.

        Parameters
        ----------
        snapshot_id : str
            Pipeline snapshot identifier.
        signals : list[dict]
            Raw detection signal dicts.  Each should have at least
            ``signal_type``, ``component``, ``created_utc``, and optionally
            ``payload_bytes`` (hex-encoded).

        Returns
        -------
        SignalGroupingReport
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SignalGroupingEngine.group_signals")

        buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for sig in signals:
            sig_type = sig.get("signal_type", "unknown")
            component = sig.get("component", "unknown")
            key = f"{sig_type}::{component}"
            buckets[key].append(sig)
        groups: list[SignalGroup] = []
        for key in sorted(buckets.keys()):
            items = buckets[key]
            sig_type, component = key.split("::", 1)
            timestamps = [
                item.get("created_utc", 0) for item in items if isinstance(item.get("created_utc"), int)
            ]
            earliest = min(timestamps) if timestamps else 0
            latest = max(timestamps) if timestamps else 0
            samples: list[bytes] = []
            for item in items[: self._max_samples]:
                payload_hex = item.get("payload_hex", "")
                if payload_hex:
                    try:
                        samples.append(bytes.fromhex(payload_hex))
                    except ValueError:
                        pass
            groups.append(
                SignalGroup(
                    group_key=key,
                    signal_type=sig_type,
                    component=component,
                    count=len(items),
                    earliest_utc=earliest,
                    latest_utc=latest,
                    sample_payloads=tuple(samples),
                )
            )
        return SignalGroupingReport(
            snapshot_id=snapshot_id,
            groups=tuple(groups),
            total_signals=len(signals),
            total_groups=len(groups),
        )


__all__ = ["SignalGroupingEngine", "SignalGroup", "SignalGroupingReport"]
