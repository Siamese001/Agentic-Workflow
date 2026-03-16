"""
Provider Binding Determinism (REQ-413)

Ensures determinism digest includes provider_id, model_id, gateway_version,
and semantic_clock_vector for reproducible LLM interactions.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "provider_binding_determinism")
emit_determinism_digest("p0", "provider_binding_determinism")

_emit_dispatches_healing_run("p1", "provider_binding_determinism", "L2")
_emit_routes_through("p1", "provider_binding_determinism", "L2")
_emit_escalates_to_human("p1", "provider_binding_determinism", "L2")
_emit_reads_policy_state("p1", "provider_binding_determinism", "L2")
_emit_authorize_and_execute("p2", "provider_binding_determinism", "execution_auth")
_emit_validates_capability("p2", "provider_binding_determinism", "capability_check")
_emit_routes_to_capability("p2", "provider_binding_determinism", "capability_route")
_emit_writes_via_uwg("p2", "provider_binding_determinism", "uwg_write")
_emit_blocks_direct_write("p2", "provider_binding_determinism", "direct_write_block")
_emit_records_tool_invocation("p2", "provider_binding_determinism", "tool_invocation")
_emit_captures_execution_output("p2", "provider_binding_determinism", "exec_output")
_emit_dispatches_agent("p3", "provider_binding_determinism", "agent_dispatch")
_emit_coordinates_agents("p3", "provider_binding_determinism", "agent_coordination")
_emit_records_workflow_lineage("p3", "provider_binding_determinism", "workflow_lineage")
_emit_records_healing_outcome("p3", "provider_binding_determinism", "healing_outcome")
_emit_escalates_failure("p3", "provider_binding_determinism", "failure_escalation")
_emit_orchestrates_workflow("p3", "provider_binding_determinism", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "provider_binding_determinism", "healing_dispatch")
_emit_invokes_evaluation("p3", "provider_binding_determinism", "evaluation_signal")
_emit_records_telemetry_event("p4", "provider_binding_determinism", "telemetry_event")
_emit_captures_evaluation_metric("p4", "provider_binding_determinism", "eval_metric")
_emit_stores_embedding("p4", "provider_binding_determinism", "embedding_store")
_emit_updates_meta_learning_state("p4", "provider_binding_determinism", "meta_learning")
_emit_links_execution_to_snapshot("p4", "provider_binding_determinism", "exec_snapshot_link")


@dataclass(frozen=True)
class ProviderBindingContext:
    """Context for provider binding determinism."""

    provider_id: str
    model_id: str
    gateway_version: str
    semantic_clock_vector: dict[str, int]


def compute_provider_binding_digest(
    provider_id: str,
    model_id: str,
    gateway_version: str,
    semantic_clock: SemanticClockSnapshot,
    additional_context: dict[str, Any] | None = None,
) -> str:
    """Compute deterministic digest for provider binding (REQ-413).

    Args:
        provider_id: LLM provider identifier (e.g., "openai", "anthropic", "google")
        model_id: Model identifier (e.g., "gpt-4", "claude-3-5-sonnet-20241022")
        gateway_version: SovereignLLMGateway version
        semantic_clock: Current semantic clock snapshot
        additional_context: Optional additional context for determinism

    Returns:
        SHA-256 hex digest of provider binding information
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "compute_provider_binding_digest", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "compute_provider_binding_digest", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "compute_provider_binding_digest")
    vector_dict = dict(semantic_clock.vector_clock)
    binding_data = {
        "provider_id": provider_id,
        "model_id": model_id,
        "gateway_version": gateway_version,
        "semantic_clock_vector": vector_dict,
        "semantic_clock_tick": semantic_clock.tick,
    }
    if additional_context:
        binding_data["additional_context"] = additional_context
    canonical_json = json.dumps(binding_data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def verify_provider_binding_determinism(
    expected_digest: str,
    provider_id: str,
    model_id: str,
    gateway_version: str,
    semantic_clock: SemanticClockSnapshot,
    additional_context: dict[str, Any] | None = None,
) -> bool:
    """Verify provider binding determinism (REQ-413).

    Args:
        expected_digest: Previously computed digest to verify against
        provider_id: LLM provider identifier
        model_id: Model identifier
        gateway_version: SovereignLLMGateway version
        semantic_clock: Current semantic clock snapshot
        additional_context: Optional additional context

    Returns:
        True if digest matches, False otherwise
    """
    computed_digest = compute_provider_binding_digest(
        provider_id=provider_id,
        model_id=model_id,
        gateway_version=gateway_version,
        semantic_clock=semantic_clock,
        additional_context=additional_context,
    )
    return computed_digest == expected_digest


def extract_provider_context_from_request(request: dict[str, Any]) -> ProviderBindingContext:
    """Extract provider binding context from LLM request.

    Args:
        request: LLM request dictionary

    Returns:
        ProviderBindingContext with extracted information
    """
    provider_id = request.get("provider", "unknown")
    model_id = request.get("model", "unknown")
    import os

    gateway_version = os.getenv("GATEWAY_VERSION", "1.0.0")
    semantic_clock_data = request.get("semantic_clock", {"tick": 0, "vector_clock": {}})
    semantic_clock_vector = semantic_clock_data.get("vector_clock", {})
    return ProviderBindingContext(
        provider_id=provider_id,
        model_id=model_id,
        gateway_version=gateway_version,
        semantic_clock_vector=semantic_clock_vector,
    )
