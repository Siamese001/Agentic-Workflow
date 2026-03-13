__version__ = "13.0"
import asyncio

from agentic_core.interfaces.gateway import GenerationRequest, SovereignLLMGateway


class GeminiLLMClient:
    """Gateway-delegating client for Gemini.  No direct SDK access."""

    _AGENT_ID = "GeminiLLMClient"
    try:
        from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig as _HTC

        _MODEL: str = _HTC().model_gemini_2_5_pro_id
    except (ImportError, AttributeError):
        _MODEL = "gemini-2.5-pro"

    def __init__(self, circuit_breaker=None):
        self._gateway = SovereignLLMGateway()
        self.circuit_breaker = circuit_breaker

    def generate(self, prompt: str) -> str:
        request = GenerationRequest(
            agent_id=self._AGENT_ID, provider="google", model=self._MODEL, prompt=prompt
        )
        response = asyncio.get_event_loop().run_until_complete(self._gateway.route_generation(request))
        return response.content
