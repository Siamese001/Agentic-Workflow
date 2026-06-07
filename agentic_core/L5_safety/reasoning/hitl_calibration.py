"""L5 HITL false-positive metric + adversarial probe escape rate.

Plan: ``docs/archive/windsurf/legacy-tree/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W9.

Closes opportunities 7.1 (HITL FP metric — fired but human approved
immediately) and 7.3 (adversarial probe regression suite + escape rate).

Two surfaces:

1. :class:`HITLCalibrationLedger` — counts HITL events partitioned by
   ``(approved, latency_bucket)`` so the dashboard can isolate "fired but
   approved instantly" — the primary signal that the trigger threshold is
   too aggressive.
2. :class:`AdversarialProbeSuite` — tracks pass/fail per probe across
   nightly runs and exposes the escape rate. ``register_probe`` adds new
   probes; ``record_outcome`` logs one run; ``escape_rate`` returns the
   fraction of probes whose latest run was a failure.

Pure data structures — no I/O. Caller persists snapshots to disk / Notion.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Final

# Latency-bucket boundaries (seconds) — coarse so dashboard cardinality
# stays bounded but covers the ranges humans actually take to approve.
_HITL_LATENCY_BUCKETS: Final[tuple[float, ...]] = (5.0, 30.0, 120.0, 600.0)


@dataclass
class HITLEvent:
    decision_id: str
    fired_reason: str
    approved: bool
    latency_seconds: float
    bucket: str = ""

    def __post_init__(self) -> None:
        # Inject the canonical bucket label
        for boundary in _HITL_LATENCY_BUCKETS:
            if self.latency_seconds <= boundary:
                object.__setattr__(self, "bucket", f"<= {boundary:g}s")
                break
        else:
            object.__setattr__(self, "bucket", f"> {_HITL_LATENCY_BUCKETS[-1]:g}s")


class HITLCalibrationLedger:
    """In-memory ledger of HITL events with FP-rate aggregation.

    Thread-safe. Caller is responsible for persistence — call
    :meth:`snapshot` to copy state for serialization.
    """

    def __init__(self) -> None:
        self._events: list[HITLEvent] = []
        self._lock = threading.Lock()

    def record(
        self,
        *,
        decision_id: str,
        fired_reason: str,
        approved: bool,
        latency_seconds: float,
    ) -> None:
        if latency_seconds < 0:
            raise ValueError("latency_seconds must be >= 0")
        ev = HITLEvent(
            decision_id=decision_id,
            fired_reason=fired_reason,
            approved=approved,
            latency_seconds=latency_seconds,
        )
        with self._lock:
            self._events.append(ev)

    def false_positive_rate(self, *, instant_threshold_seconds: float = 5.0) -> float:
        """Fraction of fired events that were approved within the threshold.

        ``approved AND latency <= threshold`` ⇒ the human did not even
        consider rejecting. That is a FP signal that the trigger fired
        without genuine concern.
        """
        with self._lock:
            if not self._events:
                return 0.0
            instant_approvals = sum(
                1
                for ev in self._events
                if ev.approved and ev.latency_seconds <= instant_threshold_seconds
            )
            return instant_approvals / len(self._events)

    def per_reason_fp_rate(
        self,
        *,
        instant_threshold_seconds: float = 5.0,
    ) -> dict[str, float]:
        """Per-fired-reason instant-approval rate. Insufficient samples → 0."""
        per_reason: dict[str, list[HITLEvent]] = {}
        with self._lock:
            for ev in self._events:
                per_reason.setdefault(ev.fired_reason, []).append(ev)
        out: dict[str, float] = {}
        for reason, events in per_reason.items():
            instant = sum(
                1
                for ev in events
                if ev.approved and ev.latency_seconds <= instant_threshold_seconds
            )
            out[reason] = instant / len(events) if events else 0.0
        return out

    def snapshot(self) -> list[HITLEvent]:
        with self._lock:
            return list(self._events)


@dataclass
class ProbeResult:
    probe_id: str
    passed: bool
    notes: str = ""


@dataclass
class AdversarialProbeSuite:
    """Track pass/fail per registered adversarial probe.

    A probe escapes when its latest recorded run did NOT pass. The escape
    rate is the fraction of registered probes currently in escape state.
    """

    _registry: set[str] = field(default_factory=set)
    _latest: dict[str, ProbeResult] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def register_probe(self, probe_id: str) -> None:
        if not probe_id:
            raise ValueError("probe_id must be non-empty")
        with self._lock:
            self._registry.add(probe_id)

    def record_outcome(self, probe_id: str, *, passed: bool, notes: str = "") -> None:
        with self._lock:
            if probe_id not in self._registry:
                raise KeyError(
                    f"probe_id={probe_id!r} not registered; "
                    "call register_probe first",
                )
            self._latest[probe_id] = ProbeResult(
                probe_id=probe_id,
                passed=passed,
                notes=notes,
            )

    def escape_rate(self) -> float:
        """Fraction of registered probes whose latest run failed.

        Probes never run yet count as PASSING (no evidence of escape) — a
        failure must be observed to count as escape.
        """
        with self._lock:
            if not self._registry:
                return 0.0
            escapes = 0
            for probe_id in self._registry:
                latest = self._latest.get(probe_id)
                if latest is not None and not latest.passed:
                    escapes += 1
            return escapes / len(self._registry)

    def escaped_probes(self) -> set[str]:
        with self._lock:
            return {
                probe_id
                for probe_id, result in self._latest.items()
                if not result.passed
            }


__all__ = [
    "AdversarialProbeSuite",
    "HITLCalibrationLedger",
    "HITLEvent",
    "ProbeResult",
]
