"""
Types for SovereignLLMGateway
"""

from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "gateway_types")
_emit_applies_guardrail("p0", "gateway_types", "p0_governance")
_emit_snapshots_state("p0", "gateway_types", "state_snapshot")

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
