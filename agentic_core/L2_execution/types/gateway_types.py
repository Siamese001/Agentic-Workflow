"""
Types for SovereignLLMGateway
"""

from dataclasses import dataclass
from typing import Any, Literal

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
