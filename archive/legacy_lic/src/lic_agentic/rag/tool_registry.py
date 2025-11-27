"""Tool registry and built-in retrieval tools."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

from .content_store import make_key


@dataclass(frozen=True)
class ToolResult:
    """Response payload returned from tool invocations."""

    content: str
    sources: List[str]
    latency_ms: int
    confidence: float


class BaseTool:
    """Base class for retrieval tools."""

    name: str = "base"
    cost: float = 0.0

    def run(self, query: str, context: Dict[str, str]) -> ToolResult:  # pragma: no cover - interface
        raise NotImplementedError

    def estimate_cost(self, query: str) -> float:
        return self.cost


class WebSearchTool(BaseTool):
    name = "web_search"
    cost = 0.5

    def run(self, query: str, context: Dict[str, str]) -> ToolResult:
        latency = _deterministic_latency(self.name, query, context, base=140, spread=60)
        snippet = f"Latest web coverage for {context.get('company_id') or 'prospect'}: {query}"
        return ToolResult(snippet, ["https://example.com/web"], latency, confidence=0.6)


class ProfileLookupTool(BaseTool):
    name = "profile_lookup"
    cost = 0.25

    def run(self, query: str, context: Dict[str, str]) -> ToolResult:
        latency = _deterministic_latency(self.name, query, context, base=95, spread=40)
        snippet = f"Profile insight about {context.get('contact_id') or 'contact'}: {query}"
        return ToolResult(snippet, ["https://example.com/profile"], latency, confidence=0.7)


class NewsTool(BaseTool):
    name = "news"
    cost = 0.4

    def run(self, query: str, context: Dict[str, str]) -> ToolResult:
        latency = _deterministic_latency(self.name, query, context, base=120, spread=50)
        snippet = f"News mention tying {context.get('company_id') or 'company'} to {query}"
        return ToolResult(snippet, ["https://example.com/news"], latency, confidence=0.65)


class ToolRegistry:
    """Registry for discovery and execution of retrieval tools."""

    def __init__(self, tools: Iterable[BaseTool] | None = None) -> None:
        self._tools: Dict[str, BaseTool] = {}
        if tools:
            for tool in tools:
                self.register(tool)

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def resolve(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered")
        return self._tools[name]

    def available(self) -> Sequence[str]:
        return tuple(sorted(self._tools.keys()))

    def make_key(self, job: Dict[str, str], context: Dict[str, str]) -> str:
        components = {
            "tool": job.get("tool"),
            "query": job.get("query"),
            "company_id": context.get("company_id"),
            "contact_id": context.get("contact_id"),
            "scope": job.get("scope", "outreach"),
            "window": context.get("window", "rolling_90d"),
        }
        return make_key(**components)

    @classmethod
    def default_with_builtins(cls) -> "ToolRegistry":
        registry = cls()
        for tool in (WebSearchTool(), ProfileLookupTool(), NewsTool()):
            registry.register(tool)
        return registry


def default_registry() -> ToolRegistry:
    """Return a registry pre-populated with built-in tools."""

    return ToolRegistry(tools=(WebSearchTool(), ProfileLookupTool(), NewsTool()))


def _deterministic_latency(name: str, query: str, context: Dict[str, str], *, base: int, spread: int) -> int:
    """Return a reproducible pseudo-latency based on the query context."""

    seed_components = [
        name,
        query,
        context.get("company_id") or "",
        context.get("contact_id") or "",
    ]
    seed = "|".join(seed_components)
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    offset = int(digest[:6], 16) % max(1, spread)
    return base + offset
