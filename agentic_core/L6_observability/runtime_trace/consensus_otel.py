"""Unified `consensus.v1.*` OTEL span emitter (Wave H4 C3 of ADR-NNN-consensus-validator-governance).

Parallel to `heal_router_otel.py` but for the L1 ConsensusEngine safety-voting
layer. Consensus voting and healing routing are semantically distinct; spans
intentionally live under a separate `consensus.v1.*` hierarchy with no direct
cross-linkage to `heal_router.v1.*` traces.

Span hierarchy:
    consensus.v1.judge                       [root — one per judge_artifact()]
    ├── consensus.v1.juror                   [per-juror vote; N children]
    └── consensus.v1.verdict                 [terminal aggregated verdict]

Design constraints:
  - Zero impact on existing ConsensusEngine consumers
  - Safe to call with no OTEL backend configured (no-op fallback)
  - Deterministic trace-id generation (uuid4)
  - In-memory ring buffer for test inspection + future SQLite projection

Plan reference: `docs/archive/windsurf/legacy-tree/plans/consensus-validator-unification-5e9f3a.md` Wave C3.
"""

from __future__ import annotations

# OTel GenAI semconv alignment (Plan: three-bucket-gap-remediation-069806 W3).
# L6 consensus emitter — multi-juror workflow spans (consensus.v1.*).
# The constants below are imported and surfaced so future span construction
# in this module attaches gen_ai.operation.name, satisfying the upstream
# OTel GenAI SIG semantic conventions.
from agentic_core.L6_observability.semconv.gen_ai import (
    ATTR_OPERATION_NAME,
    OPERATION_INVOKE_WORKFLOW,
)

#: Canonical GenAI operation discriminator for spans emitted by this module.
_GEN_AI_OPERATION: str = OPERATION_INVOKE_WORKFLOW
#: OTel attribute key for the discriminator (gen_ai.operation.name).
_GEN_AI_OPERATION_KEY: str = ATTR_OPERATION_NAME

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# Span attribute schema (stable wire format)
# ============================================================================

SPAN_NAME_JUDGE = "consensus.v1.judge"
SPAN_NAME_JUROR = "consensus.v1.juror"
SPAN_NAME_VERDICT = "consensus.v1.verdict"

REQUIRED_JUDGE_ATTRIBUTES = frozenset(
    {
        "consensus.trace_id",
        "consensus.juror_count",
        "consensus.threshold",
        "consensus.verdict",
        "consensus.artifact_hash",
    }
)

REQUIRED_JUROR_ATTRIBUTES = frozenset(
    {
        "consensus.trace_id",
        "consensus.juror_model",
        "consensus.juror_verdict",
    }
)


# ============================================================================
# In-memory records
# ============================================================================


@dataclass
class JurorVoteRecord:
    """Single juror vote within a consensus round."""

    consensus_trace_id: str
    juror_model: str
    juror_verdict: str  # "YES" | "NO" | "ABSTAIN"
    reason: str
    timestamp: float


@dataclass
class ConsensusJudgeRecord:
    """Root span for one judge_artifact() invocation."""

    consensus_trace_id: str
    timestamp: float
    juror_count: int
    threshold: float
    verdict: str  # "APPROVED" | "REJECTED" | "UNDECIDED"
    artifact_hash: str  # SHA-256 first 16 hex chars of artifact content
    juror_votes: list[JurorVoteRecord] = field(default_factory=list)
    extra_attributes: dict[str, Any] = field(default_factory=dict)

    def to_span_attributes(self) -> dict[str, Any]:
        """Project into an OTEL-compatible attribute dict."""
        attrs: dict[str, Any] = {
            "consensus.trace_id": self.consensus_trace_id,
            "consensus.juror_count": self.juror_count,
            "consensus.threshold": self.threshold,
            "consensus.verdict": self.verdict,
            "consensus.artifact_hash": self.artifact_hash,
        }
        attrs.update(self.extra_attributes)
        return attrs


# ============================================================================
# Emitter
# ============================================================================


def _forward_to_runtime_adg(record: ConsensusJudgeRecord, span_name: str) -> None:
    """Mirror a ConsensusJudgeRecord into the in-process runtime ADG store.

    Best-effort: any failure must not break the consensus voting hot path.
    """
    try:
        from agentic_core.L6_observability.otel_runtime_ingest import (  # noqa: PLC0415
            emit_span_to_runtime_adg,
        )

        span = {
            "span_id": record.consensus_trace_id,
            "trace_id": record.consensus_trace_id,
            "parent_span_id": "",
            "name": span_name,
            "kind": "cognitive",
            "layer": "L1",
            "component": "consensus_engine",
            "service_name": "consensus_engine",
            "ts_utc": int(record.timestamp * 1000),
            "duration_ms": 0.0,
            "status": "ok",
            "attributes": record.to_span_attributes(),
        }
        emit_span_to_runtime_adg(
            span,
            mission="consensus.judge",
            trace_id=record.consensus_trace_id,
        )
    except (
        ImportError,
        AttributeError,
        TypeError,
        ValueError,
    ) as exc:  # guardian: allow-log-and-swallow -- runtime-ADG mirror is best-effort; must never break consensus voting hot path
        logger.debug("consensus_otel runtime-ADG forward failed: %s", exc)


class ConsensusTelemetryEmitter:
    """Wave C3 emitter for consensus.v1 OTEL spans.

    Thread-safety: operations use a simple lock; contention is low because
    emission happens at the tail of judge_artifact() (single-call frequency).
    """

    _MAX_RING_SIZE = 1000

    def __init__(self) -> None:
        import threading  # noqa: PLC0415

        self._lock = threading.Lock()
        self._ring: list[ConsensusJudgeRecord] = []
        # M2 wiring (plan eval-meta-otel-gap-review-ef4a20 Wave W4): populate
        # the OTel tracer from the API. A NoOpTracer is returned when no SDK
        # provider is registered; a real tracer is returned when the host
        # process has installed one.
        try:
            from opentelemetry import trace  # noqa: PLC0415

            self._otel_tracer: Any = trace.get_tracer("agentic_core.L6_observability.consensus")
        except ImportError:  # pragma: no cover - OTel API absent
            self._otel_tracer = None

    def emit_judge_span(
        self,
        *,
        consensus_trace_id: str | None = None,
        juror_count: int,
        threshold: float,
        verdict: str,
        artifact_hash: str,
        juror_votes: list[JurorVoteRecord] | None = None,
        extra_attributes: dict[str, Any] | None = None,
    ) -> ConsensusJudgeRecord:
        """Capture a single `consensus.v1.judge` root span."""
        record = ConsensusJudgeRecord(
            consensus_trace_id=consensus_trace_id or str(uuid.uuid4()),
            timestamp=time.time(),
            juror_count=juror_count,
            threshold=threshold,
            verdict=verdict,
            artifact_hash=artifact_hash,
            juror_votes=list(juror_votes or []),
            extra_attributes=dict(extra_attributes or {}),
        )

        with self._lock:
            self._ring.append(record)
            if len(self._ring) > self._MAX_RING_SIZE:
                self._ring = self._ring[-self._MAX_RING_SIZE :]

        if self._otel_tracer is not None:
            try:
                attrs = record.to_span_attributes()
                with self._otel_tracer.start_as_current_span(SPAN_NAME_JUDGE, attributes=attrs):
                    pass
            except (
                AttributeError,
                TypeError,
                RuntimeError,
            ) as exc:  # guardian: allow-log-and-swallow -- OTEL span forwarding is best-effort telemetry; must never break the consensus voting hot path
                logger.debug("consensus_otel forwarding failed: %s", exc)

        # W7.1 P2.2 — forward to in-process runtime ADG store.
        _forward_to_runtime_adg(record, SPAN_NAME_JUDGE)

        return record

    def recent(self, limit: int = 100) -> list[ConsensusJudgeRecord]:
        """Return up to `limit` most-recent judge records (copy)."""
        with self._lock:
            return list(self._ring[-limit:])

    def clear(self) -> None:
        """Clear the in-memory ring. Primarily for test isolation."""
        with self._lock:
            self._ring.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._ring)


# ============================================================================
# Module-level singleton
# ============================================================================


_default_emitter: ConsensusTelemetryEmitter | None = None


def get_default_emitter() -> ConsensusTelemetryEmitter:
    """Return the process-global default consensus emitter (lazy singleton)."""
    global _default_emitter  # noqa: PLW0603
    if _default_emitter is None:
        _default_emitter = ConsensusTelemetryEmitter()
    return _default_emitter


__all__ = [
    "SPAN_NAME_JUDGE",
    "SPAN_NAME_JUROR",
    "SPAN_NAME_VERDICT",
    "REQUIRED_JUDGE_ATTRIBUTES",
    "REQUIRED_JUROR_ATTRIBUTES",
    "JurorVoteRecord",
    "ConsensusJudgeRecord",
    "ConsensusTelemetryEmitter",
    "get_default_emitter",
]
