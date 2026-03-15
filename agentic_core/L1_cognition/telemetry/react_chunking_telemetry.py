"""ReAct + Late Chunking telemetry adapter — L1_cognition seam.

Emits signals to the meta-learning bus from ReAct reasoning executions
and late-chunking pipeline runs. Uses lazy imports to avoid an upward
L1 → system_learning layer violation.

Signals emitted per execution:
  - react_performance   (trace_id, step_count, success, policy_hash)
  - retrieval_completeness (rag_context_ids, chunk_ids)
  - chunking_effectiveness (corpus_manifest_hash, chunk_count)
  - prompt_outcome_success (prompt_hash, policy_hash, success)

These feed MetaLearningBus.process_traces() via S2 telemetry.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

Logger = logging.getLogger(__name__)


def _get_meta_learning_bus():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_meta_learning_bus", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_meta_learning_bus", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L1_COGNITION, "_get_meta_learning_bus")
    from system_learning.engines.meta_learning_bus import MetaLearningBus, MetaLearningBusConfig

    return MetaLearningBus, MetaLearningBusConfig


def _build_trace_dict(
    kind: str,
    trace_id: str,
    timestamp_utc: int,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Build a minimal execution-trace dict compatible with the bus pipeline."""
    canonical = json.dumps(
        {"kind": kind, "trace_id": trace_id, "payload": payload},
        sort_keys=True,
        separators=(",", ":"),
    )
    content_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {
        "trace_id": trace_id,
        "kind": kind,
        "timestamp_utc": timestamp_utc,
        "content_hash": content_hash,
        **payload,
    }


def emit_react_performance_signal(
    trace_id: str,
    step_count: int,
    success: bool,
    policy_hash: str,
    timestamp_utc: int,
) -> dict[str, Any]:
    """Emit a react_performance telemetry signal to the meta-learning bus.

    Lazy-imports MetaLearningBus to avoid L1 → system_learning violation.
    Returns the trace dict emitted (for testing / observability).
    """
    trace = _build_trace_dict(
        kind="react_performance",
        trace_id=trace_id,
        timestamp_utc=timestamp_utc,
        payload={
            "step_count": step_count,
            "success": success,
            "policy_hash": policy_hash,
        },
    )
    _try_emit_to_bus([trace], timestamp_utc)
    return trace


def emit_retrieval_completeness_signal(
    trace_id: str,
    rag_context_ids: tuple[str, ...],
    chunk_ids: tuple[str, ...],
    timestamp_utc: int,
) -> dict[str, Any]:
    """Emit a retrieval_completeness signal to the meta-learning bus."""
    trace = _build_trace_dict(
        kind="retrieval_completeness",
        trace_id=trace_id,
        timestamp_utc=timestamp_utc,
        payload={
            "rag_context_ids": list(rag_context_ids),
            "chunk_ids": list(chunk_ids),
            "rag_count": len(rag_context_ids),
            "chunk_count": len(chunk_ids),
        },
    )
    _try_emit_to_bus([trace], timestamp_utc)
    return trace


def emit_chunking_effectiveness_signal(
    trace_id: str,
    corpus_manifest_hash: str,
    chunk_count: int,
    timestamp_utc: int,
) -> dict[str, Any]:
    """Emit a chunking_effectiveness signal to the meta-learning bus."""
    trace = _build_trace_dict(
        kind="chunking_effectiveness",
        trace_id=trace_id,
        timestamp_utc=timestamp_utc,
        payload={
            "corpus_manifest_hash": corpus_manifest_hash,
            "chunk_count": chunk_count,
        },
    )
    _try_emit_to_bus([trace], timestamp_utc)
    return trace


def emit_prompt_outcome_signal(
    trace_id: str,
    prompt_hash: str,
    policy_hash: str,
    success: bool,
    timestamp_utc: int,
) -> dict[str, Any]:
    """Emit a prompt_outcome_success signal to the meta-learning bus."""
    trace = _build_trace_dict(
        kind="prompt_outcome_success",
        trace_id=trace_id,
        timestamp_utc=timestamp_utc,
        payload={
            "prompt_hash": prompt_hash,
            "policy_hash": policy_hash,
            "success": success,
        },
    )
    _try_emit_to_bus([trace], timestamp_utc)
    return trace


def _try_emit_to_bus(traces: list[dict[str, Any]], timestamp_utc: int) -> None:
    """Attempt to process traces through MetaLearningBus — fail-open."""
    try:
        MetaLearningBus, MetaLearningBusConfig = _get_meta_learning_bus()
        bus = MetaLearningBus(config=MetaLearningBusConfig())
        bus.process_traces(traces, timestamp_utc=timestamp_utc)
    except Exception as exc:  # guardian: allow-silent-swallower
        Logger.warning(
            "react_chunking_telemetry_bus_unavailable",
            extra={"error": str(exc)},
        )


__all__ = [
    "emit_react_performance_signal",
    "emit_retrieval_completeness_signal",
    "emit_chunking_effectiveness_signal",
    "emit_prompt_outcome_signal",
]
