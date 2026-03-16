"""Concrete implementation of ChangePackage for testing and production use."""

from __future__ import annotations

from dataclasses import dataclass

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

_emit_applies_guardrail("p0", "change_package_impl", "p0_governance")
_emit_reads_policy_state("p0", "change_package_impl", "policy_binding")
_emit_snapshots_state("p0", "change_package_impl", "state_snapshot")
emit_replay_key("p0", "change_package_impl")
emit_determinism_digest("p0", "change_package_impl")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass(frozen=True, slots=True)
class ChangePackage:
    """Concrete implementation of ChangePackage protocol.

    Attributes:
        source: Source identifier for the change.
        target: Target identifier for the change.
        changes: Raw bytes representing the change.
        confidence: Confidence level (0.0 to 1.0).
        reason: Tuple of reason strings.
        timestamp_utc: UTC timestamp.
        authority_sensitivity: Authority sensitivity level (LOW/MEDIUM/HIGH).
        target_surface: Target surface identifier for mutation containment.
    """

    source: str
    target: str
    changes: bytes
    confidence: float
    reason: tuple[str, ...]
    timestamp_utc: int
    embedding_context_hash: str | None = None
    authority_sensitivity: str = "MEDIUM"
    target_surface: str | None = None

    @property
    def reasons(self) -> tuple[str, ...]:
        """Alias for reason tuple (for API compatibility)."""
        return self.reason

    def canonical_bytes(self) -> bytes:
        """Return deterministic canonical byte representation."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ChangePackage.canonical_bytes")

        import json

        return json.dumps(
            {
                "source": self.source,
                "target": self.target,
                "changes": self.changes.decode("utf-8", errors="replace"),
                "confidence": self.confidence,
                "reason": list(self.reason),
                "timestamp_utc": self.timestamp_utc,
                "embedding_context_hash": self.embedding_context_hash,
                "authority_sensitivity": self.authority_sensitivity,
                "target_surface": self.target_surface,
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
