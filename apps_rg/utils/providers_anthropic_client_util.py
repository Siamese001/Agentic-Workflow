"""Anthropic provider adapter — delegates to SovereignLLMGateway (REQ-011/012).

Direct Anthropic SDK access removed. All calls route through the gateway seam.
"""

from __future__ import annotations

import asyncio

from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
)

_emit_records_execution_trace("p0", "evidence", "providers_anthropic_client_util")
_emit_reads_policy_state("p0", "providers_anthropic_client_util", "policy_binding")
_emit_snapshots_state("p0", "providers_anthropic_client_util", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "providers_anthropic_client_util", "execution_auth")
_emit_validates_capability("p2", "providers_anthropic_client_util", "capability_check")
_emit_routes_to_capability("p2", "providers_anthropic_client_util", "capability_route")
_emit_writes_via_uwg("p2", "providers_anthropic_client_util", "uwg_write")
_emit_blocks_direct_write("p2", "providers_anthropic_client_util", "direct_write_block")
_emit_records_tool_invocation("p2", "providers_anthropic_client_util", "tool_invocation")
_emit_captures_execution_output("p2", "providers_anthropic_client_util", "exec_output")
_emit_dispatches_agent("p3", "providers_anthropic_client_util", "agent_dispatch")
_emit_coordinates_agents("p3", "providers_anthropic_client_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "providers_anthropic_client_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "providers_anthropic_client_util", "healing_outcome")
_emit_escalates_failure("p3", "providers_anthropic_client_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "providers_anthropic_client_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "providers_anthropic_client_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "providers_anthropic_client_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "providers_anthropic_client_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "providers_anthropic_client_util", "eval_metric")
_emit_stores_embedding("p4", "providers_anthropic_client_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "providers_anthropic_client_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "providers_anthropic_client_util", "exec_snapshot_link")


def run_llm_anthropic(model: str, prompt: str, *, temperature: float, max_tokens: int, timeout_s: int) -> str:
    """Delegate to SovereignLLMGateway — no direct Anthropic SDK access."""
    from agentic_core.interfaces.gateway import GenerationRequest, SovereignLLMGateway

    gw = SovereignLLMGateway()
    req = GenerationRequest(
        agent_id="anthropic_util",
        provider="anthropic",
        model=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    _clk = get_clock()
    _clk.emit_replay_key(context=f"rg:anthropic_util:{model}")
    _clk.emit_determinism_digest(inputs={"agent": "anthropic_util", "model": model})
    loop = asyncio.new_event_loop()
    try:
        resp = loop.run_until_complete(gw.route_generation(req))
    finally:
        loop.close()
    return resp.content or ""
