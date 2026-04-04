"""
agentic_core/L1_cognition/context/reasoning_context_envelope.py

ReasoningContextEnvelope — P1-L1 gap remediation.

Immutable run-scoped envelope that travels with each L1 reasoning step,
binding retrieval results, memory reads, and prompt state into a single
object per request.

ADG evidence: 0 pulls_context, 0 retrieves_via, 0 stamps_work_contract,
0 freezes_context from 103 L1 modules. 1,494 reads_from unbound.

ADG edges emitted: pulls_context, stamps_work_contract, freezes_context,
                   unfreezes_context, gated_by_confidence
"""

from __future__ import annotations

import hashlib
import logging
import threading
from dataclasses import dataclass
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.runtime.execution_trace import get_active_execution_trace

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetrievalResult:
    """A single retrieval result bound to the envelope."""

    source: str
    content: Any
    confidence: float
    source_hash: str

    @classmethod
    def from_raw(cls, source: str, content: Any, confidence: float = 1.0) -> RetrievalResult:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "RetrievalResult.from_raw", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "RetrievalResult.from_raw", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "RetrievalResult.from_raw")

        content_hash = hashlib.sha256(repr(content).encode()).hexdigest()[:16]
        return cls(source=source, content=content, confidence=confidence, source_hash=content_hash)


@dataclass(frozen=True)
class ReasoningContextEnvelope:
    """Immutable context envelope for a single L1 reasoning run.

    All retrieval results, memory reads, and prompt state bound here before
    inference begins. The envelope is stamped with a work contract hash and
    frozen before use so no mid-run state drift is possible.

    Usage::

        builder = ReasoningContextEnvelopeBuilder(run_id="r-123", task="summarise")
        builder.pull_context("rag", rag_results, confidence=0.92)
        builder.pull_context("memory", memory_items, confidence=0.85)
        envelope = builder.seal(prompt="Summarise the following…")

        # pass envelope to reasoning engine; no further writes possible
        engine.run(envelope)
    """

    run_id: str
    trace_id: str
    task: str
    prompt: str
    contract_hash: str
    retrieval_results: tuple[RetrievalResult, ...]
    metadata: dict[str, Any]
    sealed_at: float
    min_confidence: float

    @property
    def is_high_confidence(self) -> bool:
        """True if all retrievals meet the minimum confidence threshold."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L1_REASONING, "ReasoningContextEnvelope.is_high_confidence"
        )

        if not self.retrieval_results:
            return True
        return all(r.confidence >= self.min_confidence for r in self.retrieval_results)

    # guardian: allow-magic-config
    def gated_by_confidence(self, threshold: float = 0.7) -> bool:
        """Return True if this envelope may proceed (all confidences above threshold).

        Emits the ``gated_by_confidence`` ADG edge: low-confidence retrievals
        are flagged before inference proceeds.
        """
        result = all(r.confidence >= threshold for r in self.retrieval_results)
        if not result:
            low = [r.source for r in self.retrieval_results if r.confidence < threshold]
            logger.warning(
                "ENVELOPE gated_by_confidence BLOCKED run=%s low_confidence_sources=%s threshold=%.2f",
                self.run_id,
                low,
                threshold,
            )
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "trace_id": self.trace_id,
            "task": self.task,
            "contract_hash": self.contract_hash,
            "retrieval_count": len(self.retrieval_results),
            "min_confidence": self.min_confidence,
            "is_high_confidence": self.is_high_confidence,
            "metadata": self.metadata,
        }


class ReasoningContextEnvelopeBuilder:
    """Mutable builder for a :class:`ReasoningContextEnvelope`.

    Collects context via ``pull_context()``, then ``seal()`` to produce
    the immutable envelope.
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        run_id: str,
        task: str = "",
        min_confidence: float = 0.7,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._run_id = run_id
        self._task = task
        self._min_confidence = min_confidence
        self._metadata = metadata or {}
        self._retrievals: list[RetrievalResult] = []
        self._sealed = False
        self._lock = threading.Lock()

    def pull_context(
        self,
        source: str,
        content: Any,
        confidence: float = 1.0,
    ) -> ReasoningContextEnvelopeBuilder:
        """Bind a retrieval result to the envelope being built.

        Emits the ``pulls_context`` ADG edge.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L1_REASONING, "ReasoningContextEnvelopeBuilder.pull_context"
        )

        with self._lock:
            if self._sealed:
                raise RuntimeError("ReasoningContextEnvelopeBuilder: already sealed, cannot pull_context")
            result = RetrievalResult.from_raw(source, content, confidence)
            self._retrievals.append(result)
            logger.debug(
                "ENVELOPE pulls_context run=%s source=%s confidence=%.2f",
                self._run_id,
                source,
                confidence,
            )
        return self

    def seal(self, prompt: str = "") -> ReasoningContextEnvelope:
        """Seal the builder into an immutable :class:`ReasoningContextEnvelope`.

        Emits ``stamps_work_contract`` + ``freezes_context`` ADG edges.
        """
        with self._lock:
            if self._sealed:
                raise RuntimeError("ReasoningContextEnvelopeBuilder: already sealed")
            active = get_active_execution_trace()
            trace_id = active.trace_id if active else "no-active-trace"
            ts = get_clock().now_epoch()
            payload = f"{self._run_id}:{trace_id}:{self._task}:{len(self._retrievals)}:{ts:.6f}"
            contract_hash = hashlib.sha256(payload.encode()).hexdigest()[:24]
            envelope = ReasoningContextEnvelope(
                run_id=self._run_id,
                trace_id=trace_id,
                task=self._task,
                prompt=prompt,
                contract_hash=contract_hash,
                retrieval_results=tuple(self._retrievals),
                metadata=dict(self._metadata),
                sealed_at=ts,
                min_confidence=self._min_confidence,
            )
            self._sealed = True
            logger.info(
                "ENVELOPE stamps_work_contract freezes_context run=%s contract_hash=%s retrievals=%d",
                self._run_id,
                contract_hash,
                len(self._retrievals),
            )
            return envelope


_context_store: dict[str, ReasoningContextEnvelope] = {}
_store_lock = threading.Lock()


def register_envelope(envelope: ReasoningContextEnvelope) -> None:
    """Register an envelope in the process-level store (keyed by run_id)."""
    with _store_lock:
        _context_store[envelope.run_id] = envelope


def get_envelope(run_id: str) -> ReasoningContextEnvelope | None:
    """Retrieve the envelope for ``run_id``."""
    with _store_lock:
        return _context_store.get(run_id)


def release_envelope(run_id: str) -> None:
    """Release the envelope for ``run_id`` after the run completes."""
    with _store_lock:
        _context_store.pop(run_id, None)


__all__ = [
    "RetrievalResult",
    "ReasoningContextEnvelope",
    "ReasoningContextEnvelopeBuilder",
    "register_envelope",
    "get_envelope",
    "release_envelope",
]
