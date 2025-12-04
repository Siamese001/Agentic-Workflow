
"""Simple MCP registry client used for discovery and invocation stubs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence


_TRUST_ORDER = {"low": 0, "medium": 1, "high": 2}


@dataclass(frozen=True)
class ToolSpec:
    """Metadata describing a discoverable MCP tool."""

    id: str
    name: str
    capabilities: Sequence[str]
    cost: float
    trust_tier: str
    latency_ms: int
    description: str = ""

    def trust_rank(self) -> int:
        return _TRUST_ORDER.get(self.trust_tier.lower(), 0)


class MCPClient:
    """In-memory implementation of an MCP registry client."""

    def __init__(self, tools: Iterable[ToolSpec] | None = None) -> None:
        self._tools: Dict[str, ToolSpec] = {}
        for tool in tools or self._default_tools():
            self.register(tool)
        self._usage: Dict[str, int] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.id] = spec

    def discover(self, capability: str, constraints: Dict[str, object] | None = None) -> List[ToolSpec]:
        """Return tools that advertise the requested capability."""

        constraints = constraints or {}
        capability = capability.lower()
        candidates: List[ToolSpec] = []
        for spec in self._tools.values():
            if any(capability in cap.lower() for cap in spec.capabilities):
                candidates.append(spec)

        allowlist = {item.lower() for item in constraints.get("allowlist", [])}
        if allowlist:
            filtered: List[ToolSpec] = []
            for spec in candidates:
                name = spec.name.lower()
                identifier = spec.id.lower()
                if identifier in allowlist or name in allowlist:
                    filtered.append(spec)
            candidates = filtered

        denylist = {item.lower() for item in constraints.get("denylist", [])}
        if denylist:
            filtered = []
            for spec in candidates:
                identifier = spec.id.lower()
                name = spec.name.lower()
                if identifier not in denylist and name not in denylist:
                    filtered.append(spec)
            candidates = filtered

        max_cost = constraints.get("max_cost")
        if isinstance(max_cost, (int, float)):
            candidates = [spec for spec in candidates if spec.cost <= float(max_cost)]

        min_trust = constraints.get("min_trust")
        if isinstance(min_trust, str):
            min_rank = _TRUST_ORDER.get(min_trust.lower(), 0)
            candidates = [spec for spec in candidates if spec.trust_rank() >= min_rank]

        candidates.sort(key=lambda spec: (-spec.trust_rank(), spec.cost, spec.latency_ms))
        return candidates

    def invoke(self, tool_id: str, args: Dict[str, object] | None = None) -> Dict[str, object]:
        """Invoke the tool and return a deterministic stub response."""

        if tool_id not in self._tools:
            raise KeyError(f"Unknown MCP tool '{tool_id}'")
        args = args or {}
        spec = self._tools[tool_id]
        self._usage[tool_id] = self._usage.get(tool_id, 0) + 1
        query = args.get("query") or args.get("input") or ""
        content = f"{spec.name} response for {query or 'default query'}"
        return {
            "ok": True,
            "content": content,
            "usage_count": self._usage[tool_id],
            "latency_ms": spec.latency_ms,
        }

    def usage_count(self, tool_id: str) -> int:
        return self._usage.get(tool_id, 0)

    @staticmethod
    def _default_tools() -> Sequence[ToolSpec]:
        return (
            ToolSpec(
                id="web_search_v1",
                name="Web Search",
                capabilities=("web_search", "news"),
                cost=0.45,
                trust_tier="high",
                latency_ms=320,
                description="Search engine integration",
            ),
            ToolSpec(
                id="profile_lookup_v1",
                name="Profile Lookup",
                capabilities=("profile_lookup", "enrichment"),
                cost=0.3,
                trust_tier="medium",
                latency_ms=210,
                description="Enrich contact profiles",
            ),
            ToolSpec(
                id="news_digest_beta",
                name="News Digest",
                capabilities=("news", "market_intel"),
                cost=0.25,
                trust_tier="low",
                latency_ms=450,
                description="Beta digest of recent company news",
            ),
        )
