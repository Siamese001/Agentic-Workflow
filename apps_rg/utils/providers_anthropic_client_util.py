"""Anthropic provider adapter — delegates to SovereignLLMGateway (REQ-011/012).

Direct Anthropic SDK access removed. All calls route through the gateway seam.
"""

from __future__ import annotations

import asyncio

from agentic_core.L2_execution.providers import get_clock


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
