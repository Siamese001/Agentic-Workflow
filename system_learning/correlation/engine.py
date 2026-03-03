"""Risk correlation engine for deterministic multi-signal correlation."""

from __future__ import annotations

import json
from typing import Sequence

from .types import CorrelatedRiskReport, CorrelatedRow, DriftEvent


class RiskCorrelator:
    """Deterministic risk correlator for multi-signal correlation analysis."""

    def build(self, fingerprints: Sequence[str], drift_events: Sequence[DriftEvent]) -> CorrelatedRiskReport:
        """Build correlated risk report from fingerprints and drift events."""

        # Validate input
        if not isinstance(fingerprints, (list, tuple)):
            raise TypeError(f"fingerprints must be a list, got {type(fingerprints).__name__}")
        if not isinstance(drift_events, (list, tuple)):
            raise TypeError(f"drift_events must be a list, got {type(drift_events).__name__}")

        # Sort inputs for determinism
        sorted_fingerprints = sorted(fingerprints)
        sorted_drift_events = sorted(drift_events, key=lambda e: (e.policy_id, e.drift_type))

        # Generate correlated rows
        rows = []
        for fingerprint in sorted_fingerprints:
            for drift_event in sorted_drift_events:
                # Correlation rule: match if policy_id appears in fingerprint OR exact equality
                if self._should_correlate(fingerprint, drift_event.policy_id):
                    row = CorrelatedRow(
                        fingerprint=fingerprint,
                        policy_id=drift_event.policy_id,
                        drift_type=drift_event.drift_type,
                        severity=drift_event.severity,
                    )
                    rows.append(row)

        # Sort rows for stable ordering
        sorted_rows = sorted(rows, key=lambda r: (r.fingerprint, r.policy_id, r.drift_type))

        # Create canonical bytes
        canonical_data = {
            "rows": [
                {
                    "fingerprint": r.fingerprint,
                    "policy_id": r.policy_id,
                    "drift_type": r.drift_type,
                    "severity": r.severity,
                }
                for r in sorted_rows
            ],
        }
        canonical_bytes = json.dumps(canonical_data, separators=(",", ":"), sort_keys=True).encode("ascii")

        return CorrelatedRiskReport.from_canonical_bytes(sorted_rows, canonical_bytes)

    def _should_correlate(self, fingerprint: str, policy_id: str) -> bool:
        """Determine if fingerprint should correlate with policy_id."""
        # Simple correlation rule: match if policy_id appears as substring
        return policy_id in fingerprint
