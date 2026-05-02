"""Runtime trace snapshot — typed per-run OTEL / runtime-ADG summary.

Emitted AFTER ``runtime_exhaust_bundle.json`` and BEFORE
``integrated_runtime_artifact_manifest.json`` in every chain. Captures
the observable trace evidence the run actually produced:

    - run_id / request_id / trace_root (identity continuity)
    - span_count, trace_ingest_quality_score, newest_span_age_seconds
      (pulled from runtime_exhaust_bundle when available)
    - runtime_mode + detection flags (synthetic / fixture / mock)
    - detector_reasons (why the flags are what they are)
    - runtime_adg_snapshot_ref (optional — when runtime ADG is materialized)

The snapshot is the artifact the spine proof bundle's
``otel_or_runtime_trace_ref`` points at. It gives verifiers a single
first-class artifact to assert "this run produced real trace evidence,
bound to the same identity, with honest mode declarations".

Doctrine alignment:
    - No OTEL SDK coupling here. The snapshot reads fields already
      produced by the v6 exhaust pipeline + synthetic-trace detector.
    - The snapshot does NOT replace runtime ADG ingest; it summarizes
      the per-run trace surface in a single hash-bound artifact.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping

RUNTIME_TRACE_SNAPSHOT_SCHEMA_VERSION = "1.0"

_DIGEST_STABLE_FIELDS: tuple[str, ...] = (
    "schema_version",
    "run_id",
    "request_id",
    "trace_root",
    "runtime_mode",
    "synthetic_trace_detected",
    "fixture_mode_detected",
    "mock_mode_detected",
    "span_count",
    "record_count",
    "trace_ingest_quality_score",
    "detector_reasons",
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class RuntimeTraceSnapshot:
    """Typed per-run OTEL / runtime-ADG summary."""

    run_id: str
    request_id: str
    trace_root: str
    runtime_mode: str
    synthetic_trace_detected: bool
    fixture_mode_detected: bool
    mock_mode_detected: bool
    span_count: int = 0
    record_count: int = 0
    trace_ingest_quality_score: float = 1.0
    newest_span_age_seconds: float = 0.0
    detector_reasons: tuple[str, ...] = ()
    runtime_adg_snapshot_ref: str = ""
    schema_version: str = RUNTIME_TRACE_SNAPSHOT_SCHEMA_VERSION
    deterministic_digest: str = ""

    def __post_init__(self) -> None:
        for name in ("run_id", "request_id", "trace_root"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"RuntimeTraceSnapshot.{name} must be non-empty string"
                )
        if not isinstance(self.runtime_mode, str) or not self.runtime_mode:
            raise ValueError("RuntimeTraceSnapshot.runtime_mode must be non-empty")
        for name in (
            "synthetic_trace_detected",
            "fixture_mode_detected",
            "mock_mode_detected",
        ):
            if not isinstance(getattr(self, name), bool):
                raise ValueError(f"RuntimeTraceSnapshot.{name} must be bool")
        if self.schema_version != RUNTIME_TRACE_SNAPSHOT_SCHEMA_VERSION:
            raise ValueError(
                f"RuntimeTraceSnapshot.schema_version must be "
                f"{RUNTIME_TRACE_SNAPSHOT_SCHEMA_VERSION!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "runtime_mode": self.runtime_mode,
            "synthetic_trace_detected": self.synthetic_trace_detected,
            "fixture_mode_detected": self.fixture_mode_detected,
            "mock_mode_detected": self.mock_mode_detected,
            "span_count": int(self.span_count),
            "record_count": int(self.record_count),
            "trace_ingest_quality_score": float(self.trace_ingest_quality_score),
            "newest_span_age_seconds": float(self.newest_span_age_seconds),
            "detector_reasons": list(self.detector_reasons),
            "runtime_adg_snapshot_ref": self.runtime_adg_snapshot_ref,
            "deterministic_digest": self.deterministic_digest,
        }


def compute_runtime_trace_snapshot_digest(payload: Mapping[str, Any]) -> str:
    stable: dict[str, Any] = {}
    for k in _DIGEST_STABLE_FIELDS:
        v = payload.get(k)
        if isinstance(v, (list, tuple)):
            stable[k] = list(v)
        else:
            stable[k] = v
    blob = _canonical_json(stable).encode("utf-8")
    return f"sha256:{hashlib.sha256(blob).hexdigest()}"


def build_runtime_trace_snapshot(
    *,
    run_id: str,
    request_id: str,
    trace_root: str,
    runtime_mode: str,
    synthetic_trace_detected: bool,
    fixture_mode_detected: bool,
    mock_mode_detected: bool,
    span_count: int = 0,
    record_count: int = 0,
    trace_ingest_quality_score: float = 1.0,
    newest_span_age_seconds: float = 0.0,
    detector_reasons: tuple[str, ...] = (),
    runtime_adg_snapshot_ref: str = "",
) -> RuntimeTraceSnapshot:
    digest_input: dict[str, Any] = {
        "schema_version": RUNTIME_TRACE_SNAPSHOT_SCHEMA_VERSION,
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "runtime_mode": runtime_mode,
        "synthetic_trace_detected": bool(synthetic_trace_detected),
        "fixture_mode_detected": bool(fixture_mode_detected),
        "mock_mode_detected": bool(mock_mode_detected),
        "span_count": int(span_count),
        "record_count": int(record_count),
        "trace_ingest_quality_score": float(trace_ingest_quality_score),
        "detector_reasons": list(detector_reasons),
    }
    digest = compute_runtime_trace_snapshot_digest(digest_input)
    return RuntimeTraceSnapshot(
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        runtime_mode=runtime_mode,
        synthetic_trace_detected=bool(synthetic_trace_detected),
        fixture_mode_detected=bool(fixture_mode_detected),
        mock_mode_detected=bool(mock_mode_detected),
        span_count=int(span_count),
        record_count=int(record_count),
        trace_ingest_quality_score=float(trace_ingest_quality_score),
        newest_span_age_seconds=float(newest_span_age_seconds),
        detector_reasons=tuple(detector_reasons),
        runtime_adg_snapshot_ref=runtime_adg_snapshot_ref,
        deterministic_digest=digest,
    )


__all__ = [
    "RUNTIME_TRACE_SNAPSHOT_SCHEMA_VERSION",
    "RuntimeTraceSnapshot",
    "build_runtime_trace_snapshot",
    "compute_runtime_trace_snapshot_digest",
]
