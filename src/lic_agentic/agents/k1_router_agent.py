"""Router agent responsible for selecting the outreach path."""
from __future__ import annotations

from dataclasses import dataclass

from ..core import LICBaseAgent
from ..safety.bias_auditor import BiasAssessment


@dataclass(frozen=True)
class RouteDecision:
    channel: str
    priority: str


class RouterAgent(LICBaseAgent):
    """Very small heuristic-based router."""

    def __init__(self, context, *args, **kwargs):
        super().__init__(context)

    def route(self, sanitized_inputs, bias: BiasAssessment) -> RouteDecision:
        prompt = getattr(sanitized_inputs, "prompt", "")
        if "meeting" in prompt.lower():
            return RouteDecision(channel="email", priority="high")
        return RouteDecision(channel="email", priority="normal")
