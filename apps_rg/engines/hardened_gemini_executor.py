"""3.2: HardenedGeminiExecutor — Google/Gemini execution path via SovereignLLMGateway.

Wired into HardenedRouter._initialize_executors() for Provider.GOOGLE.
All calls route through SovereignLLMGateway — no direct SDK access.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class HardenedGeminiExecutor:
    """Sovereign Gemini execution path.

    Delegates all LLM calls to SovereignLLMGateway.
    Provides circuit-breaker and retry logic consistent with the hardened router.
    """

    agent_id: str = "HardenedGeminiExecutor"
    max_retries: int = 3
    _gateway: Any = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        try:
            from agentic_core.interfaces.gateway import SovereignLLMGateway

            self._gateway = SovereignLLMGateway()
        except ImportError:
            logger.warning("HardenedGeminiExecutor: SovereignLLMGateway not available")
            self._gateway = None

    def execute(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Execute a prompt via SovereignLLMGateway (Google/Gemini path).

        Returns:
            dict with 'content', 'model', 'provider', 'success' keys.
        """
        if self._gateway is None:
            raise RuntimeError("HardenedGeminiExecutor: SovereignLLMGateway not available — cannot execute")

        from agentic_core.interfaces.gateway import GenerationRequest

        effective_model = model or "gemini-2.5-pro"
        request = GenerationRequest(
            agent_id=self.agent_id,
            provider="google",
            model=effective_model,
            prompt=prompt,
        )

        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                loop = asyncio.new_event_loop()
                try:
                    response = loop.run_until_complete(self._gateway.route_generation(request))
                finally:
                    loop.close()

                logger.debug(
                    "HardenedGeminiExecutor: success on attempt %d model=%s",
                    attempt,
                    effective_model,
                )
                return {
                    "content": response.content,
                    "model": effective_model,
                    "provider": "google",
                    "success": True,
                    "attempt": attempt,
                }
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "HardenedGeminiExecutor attempt %d/%d failed: %s",
                    attempt,
                    self.max_retries,
                    exc,
                )

        raise RuntimeError(
            f"HardenedGeminiExecutor: all {self.max_retries} attempts failed. Last: {last_exc}"
        )

    def is_available(self) -> bool:
        """Return True if the gateway is wired up."""
        return self._gateway is not None


__all__ = ["HardenedGeminiExecutor"]
