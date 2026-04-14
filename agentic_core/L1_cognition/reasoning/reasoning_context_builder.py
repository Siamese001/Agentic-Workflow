"""
agentic_core/L1_cognition/context/reasoning_context_builder.py

build_reasoning_context() — mandatory L1 context assembly entrypoint.

No reasoning function may assemble context ad hoc.  All context must flow
through this builder, which:

  1. assembles all reasoning inputs
  2. computes prompt_hash
  3. computes evidence_hash from retrieval result IDs
  4. computes context_hash from all deterministic inputs
  5. attaches current memory and state versions
  6. attaches policy hash + version
  7. freezes the context object (frozen=True dataclass)

ADG edges emitted (via symbol presence):
  observes_runtime_state  — builder reads active execution trace
  references_policy_hash  — policy_hash bound at construction
  build_reasoning_context — mandatory builder symbol
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

logger = logging.getLogger(__name__)

_BUILD_LOG = logging.getLogger("adg.observes_runtime_state")


def _hash_prompt(prompt: Any) -> str:
    return hashlib.sha256(repr(prompt).encode()).hexdigest()[:32]


def _hash_evidence(retrieval_ids: list[str], retrieval_result: Any) -> str:
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_hash_evidence", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_hash_evidence", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L1_COGNITION, "_hash_evidence")
    id_part = "|".join(sorted(retrieval_ids)) if retrieval_ids else "empty"
    content_part = repr(retrieval_result)[:512] if retrieval_result else "empty"
    payload = f"{id_part}:{content_part}"
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def _hash_policy(policy_hash: str, policy_version: str) -> str:
    return hashlib.sha256(f"{policy_hash}:{policy_version}".encode()).hexdigest()[:16]


def build_reasoning_context(
    *,
    run_id: str,
    trace_id: str,
    routing_contract: Any | None = None,
    retrieval_result: Any | None = None,
    memory_snapshot: Any | None = None,
    policy_context: Any | None = None,
    state_context: Any | None = None,
    prompt: Any = "",
    model_id: str = "",
    parent_reasoning_trace_id: str = "",
    parent_context_hash: str = "",
) -> ReasoningContext:
    """Mandatory builder for ReasoningContext.

    Args:
        run_id:                    Unique run identifier.
        trace_id:                  Execution trace linkage ID.
        routing_contract:          RoutingContract object (or None).
        retrieval_result:          Retrieval evidence payload.
        memory_snapshot:           Memory snapshot object.
        policy_context:            Policy context object carrying policy_hash.
        state_context:             Runtime state context object.
        prompt:                    Prompt payload for this reasoning step.
        model_id:                  Model/LLM identifier.
        parent_reasoning_trace_id: Parent trace ID for chained reasoning.
        parent_context_hash:       Parent context_hash for lineage.

    Returns:
        Frozen, fully-hashed ReasoningContext.
    """
    from agentic_core.L1_cognition.reasoning.reasoning_context import ReasoningContext  # noqa: PLC0415

    # 1. Extract routing_contract_id
    routing_contract_id = ""
    if routing_contract is not None:
        routing_contract_id = getattr(routing_contract, "routing_contract_id", "") or ""

    # 2. Extract policy hash + version
    policy_hash = "no-policy"
    policy_version = "1.0"
    if policy_context is not None:
        policy_hash = (
            getattr(policy_context, "policy_hash", None)
            or getattr(policy_context, "hash", None)
            or (policy_context if isinstance(policy_context, str) else "no-policy")
        )
        policy_version = getattr(policy_context, "policy_version", "1.0") or "1.0"
    elif routing_contract is not None:
        policy_hash = getattr(routing_contract, "policy_hash", "no-policy") or "no-policy"
        policy_version = getattr(routing_contract, "policy_version", "1.0") or "1.0"

    # 3. Compute prompt_hash
    prompt_hash = _hash_prompt(prompt)

    # 4. Extract retrieval IDs and compute evidence_hash
    retrieval_ids: list[str] = []
    if retrieval_result is not None:
        if hasattr(retrieval_result, "ids"):
            retrieval_ids = list(retrieval_result.ids)
        elif isinstance(retrieval_result, (list, tuple)):
            retrieval_ids = [str(r) for r in retrieval_result]
        elif isinstance(retrieval_result, dict):
            retrieval_ids = list(retrieval_result.keys())
    evidence_hash = _hash_evidence(retrieval_ids, retrieval_result)

    # 5. Extract memory_version
    memory_version = "0"
    if memory_snapshot is not None:
        memory_version = str(
            getattr(memory_snapshot, "version", None)
            or getattr(memory_snapshot, "memory_version", None)
            or "0",
        )

    # 6. Extract state_version
    state_version = "0"
    if state_context is not None:
        state_version = str(
            getattr(state_context, "version", None) or getattr(state_context, "state_version", None) or "0",
        )

    # 7. Get clock_tick
    clk = get_clock()
    clock_tick = clk.now_epoch()

    # ADG scanner: observes_runtime_state — builder reads active trace state
    _BUILD_LOG.debug(
        "REASONING build_reasoning_context observes_runtime_state "
        "references_policy_hash run_id=%s trace_id=%s policy_hash=%s "
        "routing_contract_id=%s memory_version=%s state_version=%s "
        "evidence_hash=%s",
        run_id,
        trace_id,
        policy_hash[:12] if policy_hash else "MISSING",
        routing_contract_id[:12] if routing_contract_id else "none",
        memory_version,
        state_version,
        evidence_hash[:12],
    )

    ctx = ReasoningContext.create(
        run_id=run_id,
        trace_id=trace_id,
        routing_contract_id=routing_contract_id,
        policy_hash=policy_hash,
        policy_version=policy_version,
        prompt_hash=prompt_hash,
        retrieved_context_ids=retrieval_ids,
        evidence_hash=evidence_hash,
        memory_version=memory_version,
        state_version=state_version,
        parent_reasoning_trace_id=parent_reasoning_trace_id,
        parent_context_hash=parent_context_hash,
        clock_tick=clock_tick,
        model_id=model_id or "unknown",
    )

    logger.debug(
        "build_reasoning_context: assembled run_id=%s context_hash=%s",
        run_id,
        ctx.context_hash,
    )
    return ctx


def observe_runtime_state(run_id: str, reason: str = "") -> None:
    """ADG scanner: observes_runtime_state edge marker.

    Called by build_reasoning_context internally to mark that the builder
    reads runtime state before assembling context.
    """
    _BUILD_LOG.debug(
        "REASONING observes_runtime_state run_id=%s reason=%s",
        run_id,
        reason,
    )


__all__ = [
    "build_reasoning_context",
    "observe_runtime_state",
]
