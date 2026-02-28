"""RiskCorrelator — deterministic risk correlation from fingerprints + drift events."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CorrelatedRiskReport:
    fingerprint_count: int
    drift_event_count: int
    canonical_bytes: bytes

    @classmethod
    def build(cls, fingerprints: list[str], drift_events: list[Any]) -> CorrelatedRiskReport:
        canonical = json.dumps(
            {
                "drift_events": sorted(str(e) for e in drift_events),
                "fingerprints": sorted(fingerprints),
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return cls(
            fingerprint_count=len(fingerprints),
            drift_event_count=len(drift_events),
            canonical_bytes=hashlib.sha256(canonical).digest(),
        )


class RiskCorrelator:
    """Produce a deterministic CorrelatedRiskReport from fingerprints and drift events."""

    def build(
        self,
        fingerprints: list[str],
        drift_events: list[Any],
    ) -> CorrelatedRiskReport:
        if not isinstance(fingerprints, list):
            raise TypeError(f"fingerprints must be a list, got {type(fingerprints).__name__}")
        if not isinstance(drift_events, list):
            raise TypeError(f"drift_events must be a list, got {type(drift_events).__name__}")
        return CorrelatedRiskReport.build(fingerprints, drift_events)
