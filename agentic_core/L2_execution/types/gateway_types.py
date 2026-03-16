"""
Types for SovereignLLMGateway
"""

from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "gateway_types")
emit_determinism_digest("p0", "gateway_types")

_emit_dispatches_healing_run("p1", "gateway_types", "L2")
_emit_routes_through("p1", "gateway_types", "L2")
_emit_escalates_to_human("p1", "gateway_types", "L2")
_emit_reads_policy_state("p1", "gateway_types", "L2")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "gateway_types")
_emit_applies_guardrail("p0", "gateway_types", "p0_governance")
_emit_snapshots_state("p0", "gateway_types", "state_snapshot")
_emit_authorize_and_execute("p2", "gateway_types", "execution_auth")
_emit_validates_capability("p2", "gateway_types", "capability_check")
_emit_routes_to_capability("p2", "gateway_types", "capability_route")
_emit_writes_via_uwg("p2", "gateway_types", "uwg_write")
_emit_blocks_direct_write("p2", "gateway_types", "direct_write_block")
_emit_records_tool_invocation("p2", "gateway_types", "tool_invocation")
_emit_captures_execution_output("p2", "gateway_types", "exec_output")
_emit_dispatches_agent("p3", "gateway_types", "agent_dispatch")
_emit_coordinates_agents("p3", "gateway_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "gateway_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "gateway_types", "healing_outcome")
_emit_escalates_failure("p3", "gateway_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "gateway_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "gateway_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "gateway_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "gateway_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "gateway_types", "eval_metric")
_emit_stores_embedding("p4", "gateway_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "gateway_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "gateway_types", "exec_snapshot_link")

Provider = Literal["openai", "anthropic", "google"]


@dataclass
class GenerationRequest:
    """Request to the SovereignLLMGateway"""

    prompt: str
    agent_id: str
    model: str | None = None
    provider: Provider = "openai"
    temperature: float = 0.7
    max_tokens: int = 4096
    fallback_providers: list[Provider] | None = None
    token_budget_limit: int = 0
    response_schema: Any | None = None


@dataclass
class GenerationResponse:
    """Response from the SovereignLLMGateway"""

    content: str | None
    tokens: int
    provider: Provider
    model: str
    replay_envelope: str
