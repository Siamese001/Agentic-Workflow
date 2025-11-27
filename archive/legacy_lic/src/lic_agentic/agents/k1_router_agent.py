"""Router agent responsible for selecting the outreach path."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from ..safety.bias_auditor import BiasAssessment


@dataclass(frozen=True)
class RouteDecision:
    channel: str
    priority: str


class RouterAgent:
    """Very small heuristic-based router."""

    def route(self, sanitized_inputs, bias: BiasAssessment) -> RouteDecision:
        prompt = getattr(sanitized_inputs, "prompt", "")
        if "meeting" in prompt.lower():
            return RouteDecision(channel="email", priority="high")
        return RouteDecision(channel="email", priority="normal")
