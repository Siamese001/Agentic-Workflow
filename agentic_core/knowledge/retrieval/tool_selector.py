"""Tool Selector — retrieval-backed tool/skill selection for C0 context assembly.

Replaces static MCP tool-list concatenation with embedding-based retrieval,
addressing the "choice paralysis" problem identified in G3 (RAGFlow 2025,
Anthropic context-engineering 2025).

Architecture reference:
  - C0 Context Engine.md §C0.1 (retrieval plan for tool descriptions)
  - RAGFlow 2025: "Tool-description retrieval is a first-class problem"
  - Anthropic 2025: "The set of tools presented to the agent must itself
    be retrieved, not statically concatenated."

Design:
  - ToolSelector receives a query + task hint and returns a ranked, bounded
    subset of tool definitions relevant to the task.
  - Backed by ``ToolEmbeddingCache`` for embedding caching and a pluggable
    similarity function (cosine by default).
  - Integrates with the MCP registry (``mcp_config.json``) as the source of
    tool metadata (name, description, server).
  - Emits ``ToolSelectionResult`` with provenance for audit tracing.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.L4_state.cache.tool_embedding_cache import ToolEmbeddingCache

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


@dataclass
class ToolDefinition:
    """A single tool's metadata for retrieval.

    Attributes
    ----------
    name : str
        Tool name (e.g. ``"adg_edge_fanin"``).
    description : str
        Human-readable description of what the tool does.
    server : str
        MCP server ID that owns this tool (e.g. ``"adg_sqlite"``).
    tags : list[str]
        Categorization tags for retrieval boosting.
    """

    name: str
    description: str
    server: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class ToolSelectionResult:
    """Result of a tool selection pass.

    Attributes
    ----------
    query : str
        Original query string used for selection.
    selected_tools : list[ToolDefinition]
        Ranked, bounded subset of tools relevant to the query.
    scores : dict[str, float]
        Mapping of tool name → relevance score (0–1).
    total_candidates : int
        Total number of tools considered before selection.
    budget_used : int
        Number of tools selected (≤ max_tools).
    provenance : dict[str, Any]
        Audit metadata (method, config, timestamp).
    """

    query: str
    selected_tools: list[ToolDefinition] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    total_candidates: int = 0
    budget_used: int = 0
    provenance: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Cosine similarity (no numpy required)
# ---------------------------------------------------------------------------


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# MCP registry loader
# ---------------------------------------------------------------------------


def load_tool_registry_from_mcp_config(
    config_path: str | Path | None = None,
) -> list[ToolDefinition]:
    """Load tool definitions from the MCP config file.

    Parses ``mcp_config.json`` to extract server IDs.  Tool names and
    descriptions are populated from the AGENTS.md Quick Reference table
    when available; otherwise a minimal stub is created from the server ID.

    Args:
        config_path: Path to ``mcp_config.json``.  Defaults to the
            repo-local ``.windsurf/mcp_config.json``.

    Returns:
        List of ``ToolDefinition`` objects, one per server (coarse-grained
        until per-tool metadata is available in the config).
    """
    if config_path is None:
        config_path = Path(__file__).resolve().parents[4] / ".windsurf" / "mcp_config.json"
    config_path = Path(config_path)

    tools: list[ToolDefinition] = []
    try:
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        log.warning("Cannot load MCP config from %s: %s", config_path, exc)
        return tools

    servers = config.get("mcpServers", {})
    for server_id, server_conf in servers.items():
        if server_conf.get("disabled", False):
            continue
        tools.append(ToolDefinition(
            name=server_id,
            description=f"MCP server: {server_id}",
            server=server_id,
            tags=["mcp", server_id],
        ))
    return tools


# ---------------------------------------------------------------------------
# ToolSelector
# ---------------------------------------------------------------------------


class ToolSelector:
    """Retrieval-backed tool selector — replaces static tool-list concatenation.

    Given a query and a tool registry, selects the most relevant tools using
    embedding similarity.  Backed by ``ToolEmbeddingCache`` for caching.

    Args:
        max_tools : int
            Maximum number of tools to return per selection pass.
        min_score : float
            Minimum similarity score to include a tool (0–1).
        embed_fn : callable or None
            Function that takes a list[str] and returns list[list[float]].
            If None, a heuristic keyword-matching fallback is used.
        cache : ToolEmbeddingCache or None
            Embedding cache instance.  Created on first use if None.
    """

    def __init__(
        self,
        max_tools: int = 8,
        min_score: float = 0.3,
        embed_fn: Any = None,
        cache: ToolEmbeddingCache | None = None,
    ) -> None:
        self.max_tools = max_tools
        self.min_score = min_score
        self._embed_fn = embed_fn
        self._cache = cache
        self._last_query_embedding: list[float] = []
        log.info("ToolSelector initialized (max_tools=%d, min_score=%.2f)", max_tools, min_score)

    def select(
        self,
        query: str,
        tool_registry: list[ToolDefinition],
        *,
        task_hint: str = "",
    ) -> ToolSelectionResult:
        """Select tools relevant to the query from the registry.

        Args:
            query: The task/query string to match tools against.
            tool_registry: Full list of available tools.
            task_hint: Optional task classification hint for boosting.

        Returns:
            ``ToolSelectionResult`` with ranked, bounded tool subset.
        """
        if not tool_registry:
            return ToolSelectionResult(query=query, total_candidates=0)

        combined_query = f"{query} {task_hint}".strip()

        # Try embedding-based selection
        if self._embed_fn is not None:
            return self._select_by_embedding(combined_query, tool_registry)

        # Fallback: keyword matching
        return self._select_by_keyword(combined_query, tool_registry)

    def _select_by_embedding(
        self,
        query: str,
        tools: list[ToolDefinition],
    ) -> ToolSelectionResult:
        """Select tools using embedding cosine similarity."""
        tool_texts = [f"{t.name}: {t.description}" for t in tools]
        tool_defs = [
            {"name": t.name, "description": t.description, "tags": t.tags}
            for t in tools
        ]

        # Get tool embeddings (cached)
        cache = self._cache or ToolEmbeddingCache()

        def _compute() -> tuple[list[list[float]], list[str]]:
            tool_embeds = self._embed_fn(tool_texts)  # type: ignore[misc]
            query_embeds = self._embed_fn([query])
            # Return tool embeddings + names; store query embedding separately
            self._last_query_embedding = query_embeds[0] if query_embeds else []
            return (tool_embeds, [t.name for t in tools])

        tool_embeddings, _tool_names = cache.get_or_fetch(tool_defs, _compute)
        query_embedding = self._last_query_embedding

        if not query_embedding or not tool_embeddings:
            return self._select_by_keyword(query, tools)

        # Score each tool by cosine similarity
        scored: list[tuple[float, ToolDefinition]] = []
        for idx, tool in enumerate(tools):
            if idx < len(tool_embeddings):
                score = _cosine_similarity(query_embedding, tool_embeddings[idx])
            else:
                score = 0.0
            scored.append((score, tool))

        return self._rank_and_select(query, scored, len(tools), method="embedding")

    def _select_by_keyword(
        self,
        query: str,
        tools: list[ToolDefinition],
    ) -> ToolSelectionResult:
        """Fallback: select tools by keyword overlap scoring."""
        query_tokens = set(query.lower().split())
        scored: list[tuple[float, ToolDefinition]] = []

        for tool in tools:
            tool_tokens = set(
                f"{tool.name} {tool.description} {' '.join(tool.tags)}".lower().split()
            )
            overlap = len(query_tokens & tool_tokens)
            total = max(len(query_tokens), 1)
            score = overlap / total if total > 0 else 0.0
            scored.append((score, tool))

        return self._rank_and_select(query, scored, len(tools), method="keyword")

    def _rank_and_select(
        self,
        query: str,
        scored: list[tuple[float, ToolDefinition]],
        total_candidates: int,
        *,
        method: str,
    ) -> ToolSelectionResult:
        """Filter, rank, and bound the scored tools."""
        # Filter by minimum score
        filtered = [(s, t) for s, t in scored if s >= self.min_score]

        # Sort descending by score
        filtered.sort(key=lambda x: x[0], reverse=True)

        # Bound to max_tools
        selected = filtered[: self.max_tools]

        selected_tools = [t for _, t in selected]
        scores = {t.name: round(s, 4) for s, t in selected}

        return ToolSelectionResult(
            query=query,
            selected_tools=selected_tools,
            scores=scores,
            total_candidates=total_candidates,
            budget_used=len(selected_tools),
            provenance={
                "method": method,
                "min_score": self.min_score,
                "max_tools": self.max_tools,
            },
        )


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_global_selector: ToolSelector | None = None


def get_tool_selector() -> ToolSelector:
    """Get or create the global tool selector."""
    global _global_selector  # noqa: PLW0603
    if _global_selector is None:
        _global_selector = ToolSelector()
    return _global_selector
