"""
W4-C Shadow Drift Analyzer

Converts W4-B shadow telemetry into deterministic drift signals.
Provides informational-only policy feedback without automatic mutation.
"""

import hashlib
import json
import statistics
from dataclasses import dataclass
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

_DEFAULT_DRIFT_THRESHOLD = 0.92


@dataclass(frozen=True, slots=True)
class DriftSummary:
    """Summary of shadow embedding drift analysis."""

    profile_id: str
    batch_size: int
    mean_cosine: float  # 6-decimal rounded
    p95_cosine: float  # 6-decimal rounded
    drift_flag: bool
    drift_score: float  # bounded 0.0-1.0
    deterministic_digest: str  # SHA-256 of canonical data
    drift_threshold: float = _DEFAULT_DRIFT_THRESHOLD  # externalized, L4-governable

    def emit_digest(self) -> None:
        """Print the drift digest for determinism verification."""
        print(f"W4C-DRIFT-DIGEST: {self.deterministic_digest}")

    def to_canonical_json(self) -> str:
        """Convert to canonical JSON for deterministic serialization."""
        # Round to 6 decimal places for consistency
        data = {
            "profile_id": self.profile_id,
            "batch_size": self.batch_size,
            "mean_cosine": round(self.mean_cosine, 6),
            "p95_cosine": round(self.p95_cosine, 6),
            "drift_flag": self.drift_flag,
            "drift_score": round(self.drift_score, 6),
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"))


class ShadowDriftAnalyzer:
    """Analyzes shadow embedding telemetry for drift detection."""

    def __init__(self, drift_threshold: float = _DEFAULT_DRIFT_THRESHOLD) -> None:
        self._drift_threshold = drift_threshold

    def analyze_batch(
        self,
        *,
        shadow_records: list[dict[str, Any]],
        profile_id: str,
        now_utc: int,
    ) -> DriftSummary:
        """Analyze a batch of shadow telemetry records for drift.

        Args:
            shadow_records: List of shadow telemetry dictionaries
            profile_id: RetrievalProfile identifier
            now_utc: Current timestamp

        Returns:
            DriftSummary with deterministic digest
        """
        if not shadow_records:
            # Empty batch - return neutral drift
            return DriftSummary(
                profile_id=profile_id,
                batch_size=BATCH_SIZE,
                mean_cosine=1.0,
                p95_cosine=1.0,
                drift_flag=False,
                drift_score=0.0,
                deterministic_digest=self._compute_digest([], profile_id, now_utc),
            )

        # Extract cosine similarities with stable ordering
        cosine_values = []
        for record in shadow_records:
            if "primary_shadow_cosine" in record:
                cosine_values.append(float(record["primary_shadow_cosine"]))

        if not cosine_values:
            # No cosine data - return neutral drift
            return DriftSummary(
                profile_id=profile_id,
                batch_size=len(shadow_records),
                mean_cosine=1.0,
                p95_cosine=1.0,
                drift_flag=False,
                drift_score=0.0,
                deterministic_digest=self._compute_digest([], profile_id, now_utc),
            )

        # Sort for deterministic aggregation
        cosine_values.sort()

        # Compute statistics with 6-decimal rounding
        mean_cosine = round(statistics.mean(cosine_values), 6)
        p95_cosine = round(self._compute_percentile(cosine_values, 0.95), 6)

        # Apply deterministic drift rule (threshold externalized via constructor)
        drift_flag = p95_cosine < self._drift_threshold
        drift_score = round(max(0.0, min(1.0, 1.0 - p95_cosine)), 6)

        # Compute deterministic digest
        deterministic_digest = self._compute_digest(cosine_values, profile_id, now_utc)

        summary = DriftSummary(
            profile_id=profile_id,
            batch_size=len(shadow_records),
            mean_cosine=mean_cosine,
            p95_cosine=p95_cosine,
            drift_flag=drift_flag,
            drift_score=drift_score,
            deterministic_digest=deterministic_digest,
            drift_threshold=self._drift_threshold,
        )

        # P5-5B: Emit to DriftRegistry; P5-5C: critical → MetaLearningBus
        self._emit_to_registry(summary)

        return summary

    def _emit_to_registry(self, summary: DriftSummary) -> None:
        """Emit shadow drift measurement to unified DriftRegistry (P5-5B/5C)."""
        try:
            import hashlib
            import json as _json

            from agentic_core.L6_observability.engines.drift_registry import (
                DriftRegistryEntry,
                get_drift_registry,
            )

            severity = "critical" if summary.drift_flag else "info"
            digest_payload = _json.dumps(
                {
                    "source": "shadow",
                    "metric": "p95_cosine",
                    "value": summary.p95_cosine,
                    "threshold": summary.drift_threshold,
                    "digest": summary.deterministic_digest,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            deterministic_digest = hashlib.sha256(digest_payload.encode()).hexdigest()

            entry = DriftRegistryEntry(
                source="shadow",  # type: ignore[arg-type]
                timestamp_iso=_json.dumps(summary.profile_id),  # no timestamp on DriftSummary; use profile_id as tag
                metric_name="p95_cosine",
                current_value=summary.p95_cosine,
                threshold_value=summary.drift_threshold,
                drift_flag=summary.drift_flag,
                severity=severity,  # type: ignore[arg-type]
                deterministic_digest=deterministic_digest,
            )
            get_drift_registry().record(entry)

            # P5-5C: critical → MetaLearningBus
            if summary.drift_flag:
                try:
                    from system_learning.ports.meta_learning_bus import MetaLearningBus
                    from system_learning.ports.meta_learning_change_package import (
                        MetaLearningChangePackage,
                    )

                    bus = MetaLearningBus.get_instance()
                    pkg = MetaLearningChangePackage.create(
                        kind="drift_alert",
                        payload={
                            "source": "shadow",
                            "metric_name": "p95_cosine",
                            "current_value": summary.p95_cosine,
                            "threshold_value": summary.drift_threshold,
                            "severity": severity,
                            "drift_score": summary.drift_score,
                            "digest": summary.deterministic_digest,
                            "profile_id": summary.profile_id,
                        },
                        proposal_only=True,
                    )
                    bus.enqueue(pkg)
                except Exception:  # guardian: allow-silent-swallow
                    pass
        except Exception:  # guardian: allow-silent-swallow
            pass

    def _compute_percentile(self, values: list[float], percentile: float) -> float:
        """Compute percentile with deterministic method."""
        if not values:
            return 0.0

        sorted_values = sorted(values)
        n = len(sorted_values)

        if n == 1:
            return sorted_values[0]

        # Linear interpolation for percentile
        index = percentile * (n - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, n - 1)
        fraction = index - lower_index

        lower_value = sorted_values[lower_index]
        upper_value = sorted_values[upper_index]

        return lower_value + fraction * (upper_value - lower_value)

    def _compute_digest(self, cosine_values: list[float], profile_id: str, now_utc: int) -> str:
        """Compute deterministic SHA-256 digest of analysis data."""
        # Create canonical representation
        data = {
            "profile_id": profile_id,
            "now_utc": now_utc,
            "cosine_values": [round(v, 6) for v in sorted(cosine_values)],
            "drift_threshold": self._drift_threshold,
        }

        # Serialize to canonical JSON
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))

        # Compute SHA-256 digest
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# Export public interface
__all__ = [
    "ShadowDriftAnalyzer",
    "DriftSummary",
]
