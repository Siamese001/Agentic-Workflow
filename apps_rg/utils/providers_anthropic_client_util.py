"""Anthropic provider adapter — delegates to SovereignLLMGateway (REQ-011/012).

Direct Anthropic SDK access removed. All calls route through the gateway seam.
"""

from __future__ import annotations

import asyncio


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def run_llm_anthropic(
    model: str,
    prompt: str,
    *,
    temperature: float,
    max_tokens: int,
    timeout_s: int,
) -> str:
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
    loop = asyncio.new_event_loop()
    try:
        resp = loop.run_until_complete(gw.route_generation(req))
    finally:
        loop.close()
    return resp.content or ""
