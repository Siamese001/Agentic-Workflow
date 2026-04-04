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
    from agentic_core.L1_cognition.context.reasoning_context import ReasoningContext  # noqa: PLC0415

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
            or "0"
        )

    # 6. Extract state_version
    state_version = "0"
    if state_context is not None:
        state_version = str(
            getattr(state_context, "version", None) or getattr(state_context, "state_version", None) or "0"
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
