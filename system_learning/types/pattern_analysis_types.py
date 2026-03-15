"""Pattern Analysis Types - Phase 8.

Frozen dataclasses for deterministic pattern analysis findings.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass(frozen=True, slots=True)
class PatternSourceIds:
    """Identifiers for source data used in pattern analysis."""

    healing_snapshot_version: str
    detection_signal_version: str | None = None
    drift_snapshot_version: str | None = None


@dataclass(frozen=True, slots=True)
class PatternFindingKey:
    """Key for a pattern finding."""

    component: str
    dimension: str
    label: str


@dataclass(frozen=True, slots=True)
class PatternFinding:
    """A single pattern finding with deterministic evidence."""

    key: PatternFindingKey
    severity: float
    evidence: tuple[str, ...]
    metrics: tuple[tuple[str, float], ...]

    def canonical_bytes(self) -> bytes:
        """Generate canonical byte representation."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PatternFinding.canonical_bytes")

        data = {
            "component": self.key.component,
            "dimension": self.key.dimension,
            "label": self.key.label,
            "severity": round(self.severity, 6),
            "evidence": tuple(sorted(self.evidence)),
            "metrics": tuple(((name, round(value, 6)) for name, value in sorted(self.metrics))),
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        """Generate SHA256 hash of canonical content."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class PatternFindingReport:
    """Complete pattern analysis report."""

    source_ids: PatternSourceIds
    findings: tuple[PatternFinding, ...]

    def canonical_bytes(self) -> bytes:
        """Generate canonical byte representation."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PatternFindingReport.canonical_bytes")

        data = {
            "healing_snapshot_version": self.source_ids.healing_snapshot_version,
            "detection_signal_version": self.source_ids.detection_signal_version,
            "drift_snapshot_version": self.source_ids.drift_snapshot_version,
            "findings": [
                {
                    "component": f.key.component,
                    "dimension": f.key.dimension,
                    "label": f.key.label,
                    "severity": round(f.severity, 6),
                    "evidence": tuple(sorted(f.evidence)),
                    "metrics": tuple(((name, round(value, 6)) for name, value in sorted(f.metrics))),
                }
                for f in self.findings
            ],
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        """Generate SHA256 hash of canonical content."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
