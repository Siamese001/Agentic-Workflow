"""RiskCorrelator — deterministic risk correlation from fingerprints + drift events."""

from __future__ import annotations

import json
from typing import Any

from system_learning.engines.correlation.types import CorrelatedRiskReport, CorrelatedRow


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

        rows: list[CorrelatedRow] = []
        for fp in fingerprints:
            for event in drift_events:
                policy_id = getattr(event, "policy_id", None) or str(event)
                if policy_id in fp:
                    rows.append(
                        CorrelatedRow(
                            fingerprint=fp,
                            policy_id=policy_id,
                            drift_type=getattr(event, "drift_type", "UNKNOWN"),
                            severity=float(getattr(event, "severity", 0.0)),
                        )
                    )

        rows = sorted(rows, key=lambda r: (r.fingerprint, r.policy_id, r.drift_type))

        canonical = json.dumps(
            {
                "drift_events": sorted(
                    json.dumps(
                        {
                            "drift_type": getattr(e, "drift_type", ""),
                            "policy_id": getattr(e, "policy_id", str(e)),
                        },
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    for e in drift_events
                ),
                "fingerprints": sorted(fingerprints),
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return CorrelatedRiskReport.from_canonical_bytes(rows=rows, canonical_bytes=canonical)
