"""Anthropic provider adapter — delegates to SovereignLLMGateway (REQ-011/012).

Direct Anthropic SDK access removed. All calls route through the gateway seam.
"""

from __future__ import annotations

import asyncio

from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "providers_anthropic_client_util")
_emit_reads_policy_state("p0", "providers_anthropic_client_util", "policy_binding")
_emit_snapshots_state("p0", "providers_anthropic_client_util", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
