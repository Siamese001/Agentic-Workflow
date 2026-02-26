# File: GeminiLLMClient.py
# Description: Gemini LLM client — delegates ALL calls through SovereignLLMGateway

__version__ = "13.0"

import asyncio

from agentic_core.interfaces.gateway import GenerationRequest, SovereignLLMGateway


class GeminiLLMClient:
    """Gateway-delegating client for Gemini.  No direct SDK access."""

    _AGENT_ID = "GeminiLLMClient"
    _MODEL = "gemini-pro"

    def __init__(self, circuit_breaker=None):
        self._gateway = SovereignLLMGateway()
        self.circuit_breaker = circuit_breaker  # kept for API compat; unused internally

    def generate(self, prompt: str) -> str:
        request = GenerationRequest(
            agent_id=self._AGENT_ID,
            provider="google",
            model=self._MODEL,
            prompt=prompt,
        )
        response = asyncio.get_event_loop().run_until_complete(self._gateway.route_generation(request))
        return response.content
