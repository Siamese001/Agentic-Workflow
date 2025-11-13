"""Selection logic for MCP-discovered tools."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

from ..core import PolicyController
from ..mcp import MCPClient, ToolSpec

_TRUST_SCORE = {"low": 0.4, "medium": 0.7, "high": 1.0}


@dataclass(frozen=True)
class SelectedTool:
    """Tool selection decision returned by :class:`MCPSelector`."""

    spec: ToolSpec
    score: float
    quarantined: bool
    budget_multiplier: float


class MCPSelector:
    """Rank tools from the MCP registry using trust and policy signals."""

    def __init__(self, client: MCPClient, policy: PolicyController, *, allowlist: Iterable[str] | None = None) -> None:
        self._client = client
        self._policy = policy
        self._allowlist = {item.lower() for item in (allowlist or [])}
        self._promoted: Dict[str, bool] = {}

    @property
    def client(self) -> MCPClient:
        return self._client

    @property
    def policy(self) -> PolicyController:
        return self._policy

    def discover(self, capability: str, constraints: Dict[str, object] | None = None) -> List[SelectedTool]:
        """Return ranked tools that satisfy the provided constraints."""

        specs = self._client.discover(capability, constraints)
        selections: List[SelectedTool] = []
        for spec in specs:
            if self._allowlist and spec.id.lower() not in self._allowlist and spec.name.lower() not in self._allowlist:
                continue
            quarantined = self.policy.quarantine_status(spec.id) or not self._promoted.get(spec.id, False)
            score = self._score(spec, quarantined)
            budget = self.policy.budget_multiplier * (0.7 if quarantined else 1.0)
            selections.append(
                SelectedTool(
                    spec=spec,
                    score=score,
                    quarantined=quarantined,
                    budget_multiplier=budget,
                )
            )
        selections.sort(key=lambda item: item.score, reverse=True)
        return selections

    def mark_promoted(self, tool_id: str) -> None:
        self._promoted[tool_id] = True
        self.policy.promote_tool(tool_id)

    def quarantine(self, tool_id: str) -> None:
        self._promoted[tool_id] = False
        self.policy.set_quarantine(tool_id)

    def _score(self, spec: ToolSpec, quarantined: bool) -> float:
        trust = _TRUST_SCORE.get(spec.trust_tier.lower(), 0.2)
        cost_factor = max(0.1, 1.2 - spec.cost)
        latency_factor = max(0.2, 1.0 - spec.latency_ms / 2000)
        penalty = 0.6 if quarantined else 1.0
        return trust * cost_factor * latency_factor * penalty


def register_discovered_tools(
    registry,
    selector: MCPSelector,
    capability: str,
    constraints: Dict[str, object] | None = None,
) -> Sequence[SelectedTool]:
    """Discover tools and register them with the given registry."""

    selections = selector.discover(capability, constraints)
    for selection in selections:
        tool_id = selection.spec.id
        selector.policy.register_tool(tool_id, quarantined=selection.quarantined)
        if tool_id not in registry.available():
            from .tool_registry import BaseTool, ToolResult

            class MCPToolAdapter(BaseTool):
                name = tool_id
                cost = selection.spec.cost

                def run(self, query: str, context: Dict[str, str]) -> ToolResult:  # type: ignore[name-defined]
                    response = selector.client.invoke(tool_id, {"query": query, **context})
                    content = response["content"]
                    latency = response["latency_ms"]
                    sources = [f"mcp://{tool_id}"]
                    return ToolResult(content, sources, latency, confidence=0.6)

            registry.register(MCPToolAdapter())
    return selections
