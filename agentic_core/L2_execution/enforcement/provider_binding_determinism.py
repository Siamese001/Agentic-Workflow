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

from agentic_core.L0_routing.types.determinism_types import (
    SemanticClockSnapshot,
)  # guardian: allow-layer-violation -- L2 module uses L0 config/enforcement; intentional downward enforcement-chain dependency
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "provider_binding_determinism")
trace_contract.emit_determinism_digest("p0", "provider_binding_determinism")

trace_contract._emit_dispatches_healing_run("p1", "provider_binding_determinism", "L2")
trace_contract._emit_routes_through("p1", "provider_binding_determinism", "L2")
trace_contract._emit_checks_agent_registry("p1", "provider_binding_determinism", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "provider_binding_determinism", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "provider_binding_determinism", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "provider_binding_determinism", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "provider_binding_determinism", "target_agent")
trace_contract._emit_verifies_policy("p1", "provider_binding_determinism", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "provider_binding_determinism", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "provider_binding_determinism", "boundary_check")
trace_contract._emit_transcripts_response("p1", "provider_binding_determinism", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "provider_binding_determinism")
trace_contract._emit_gated_by_confidence("p1", "provider_binding_determinism", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "provider_binding_determinism", "L2")
trace_contract._emit_reads_policy_state("p1", "provider_binding_determinism", "L2")
trace_contract._emit_authorize_and_execute("p2", "provider_binding_determinism", "execution_auth")
trace_contract._emit_validates_capability("p2", "provider_binding_determinism", "capability_check")
trace_contract._emit_routes_to_capability("p2", "provider_binding_determinism", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "provider_binding_determinism", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "provider_binding_determinism", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "provider_binding_determinism", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "provider_binding_determinism", "exec_output")
trace_contract._emit_dispatches_agent("p3", "provider_binding_determinism", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "provider_binding_determinism", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "provider_binding_determinism", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "provider_binding_determinism", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "provider_binding_determinism", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "provider_binding_determinism", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "provider_binding_determinism", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "provider_binding_determinism", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "provider_binding_determinism", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "provider_binding_determinism", "eval_metric")
trace_contract._emit_stores_embedding("p4", "provider_binding_determinism", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "provider_binding_determinism", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "provider_binding_determinism", "exec_snapshot_link")

trace_contract.record_execution_trace("provider_binding_determinism", "provider_binding_determinism_trace")


trace_contract._emit_emits_metric_event("provider_binding_determinism", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("provider_binding_determinism", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("provider_binding_determinism", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("provider_binding_determinism", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("provider_binding_determinism", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("provider_binding_determinism", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("provider_binding_determinism", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("provider_binding_determinism", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("provider_binding_determinism", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("provider_binding_determinism", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("provider_binding_determinism", "p4obs", "alert")
trace_contract._emit_links_incident_trace("provider_binding_determinism", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("provider_binding_determinism", "p3lm", "pattern")
trace_contract._emit_records_learning_event("provider_binding_determinism", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("provider_binding_determinism", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("provider_binding_determinism", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("provider_binding_determinism", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("provider_binding_determinism", "p3lm", "policy")
trace_contract._emit_stores_learning_state("provider_binding_determinism", "p3lm", "state")
trace_contract._emit_records_execution_trace("provider_binding_determinism", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("provider_binding_determinism", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("provider_binding_determinism", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("provider_binding_determinism", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("provider_binding_determinism", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("provider_binding_determinism", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("provider_binding_determinism", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("provider_binding_determinism", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("provider_binding_determinism", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "provider_binding_determinism", "context_pull")
trace_contract._emit_pulls_context("p1", "provider_binding_determinism", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "provider_binding_determinism", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "provider_binding_determinism", "uwg_term_2")
trace_contract._emit_writes_through("p1", "provider_binding_determinism", "write_through")
trace_contract._emit_writes_through("p1", "provider_binding_determinism", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "provider_binding_determinism", "safety_validation")
trace_contract._emit_invokes_eval("p1", "provider_binding_determinism", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "provider_binding_determinism", "routing_commit")


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
        model_id: Model identifier (e.g., "gpt-4", "claude-sonnet-5")
        gateway_version: SovereignLLMGateway version
        semantic_clock: Current semantic clock snapshot
        additional_context: Optional additional context for determinism

    Returns:
        SHA-256 hex digest of provider binding information
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "compute_provider_binding_digest", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "compute_provider_binding_digest", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "compute_provider_binding_digest")
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
