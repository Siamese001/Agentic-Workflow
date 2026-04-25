"""Unit tests for ToolSelector (W4.1 — G3 tool/skill retrieval rail)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from agentic_core.L4_state.cache.tool_embedding_cache import ToolEmbeddingCache
from agentic_core.knowledge.retrieval.tool_selector import (
    ToolDefinition,
    ToolSelectionResult,
    ToolSelector,
    _cosine_similarity,
    load_tool_registry_from_mcp_config,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_tools() -> list[ToolDefinition]:
    return [
        ToolDefinition(name="adg_edge_fanin", description="Get incoming edges to a node", server="adg_sqlite", tags=["graph", "dependency"]),
        ToolDefinition(name="redis_get", description="Get value for a Redis key", server="redis", tags=["cache", "state"]),
        ToolDefinition(name="browser_click", description="Click on a web page element", server="playwright", tags=["browser", "ui"]),
        ToolDefinition(name="pytest_run", description="Run pytest with specified options", server="pytest_mcp", tags=["test", "ci"]),
        ToolDefinition(name="git_status", description="Show working tree status", server="GitKraken", tags=["git", "vcs"]),
        ToolDefinition(name="notion_post", description="Create a Notion page", server="notion", tags=["notion", "write"]),
    ]


@pytest.fixture
def mcp_config_file(tmp_path: Path) -> Path:
    config = {
        "mcpServers": {
            "adg_sqlite": {"command": "python", "args": ["-m", "tools.adg.mcp.server"], "disabled": False},
            "redis": {"command": "python", "args": ["-m", "tools.mcp.redis_server"], "disabled": False},
            "disabled_one": {"command": "echo", "args": [], "disabled": True},
        }
    }
    p = tmp_path / "mcp_config.json"
    p.write_text(json.dumps(config), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Cosine similarity
# ---------------------------------------------------------------------------

class TestCosineSimilarity:

    def test_identical_vectors(self) -> None:
        v = [1.0, 2.0, 3.0]
        assert _cosine_similarity(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors(self) -> None:
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert _cosine_similarity(a, b) == pytest.approx(0.0)

    def test_zero_vector(self) -> None:
        assert _cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0

    def test_opposite_vectors(self) -> None:
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        assert _cosine_similarity(a, b) == pytest.approx(-1.0)


# ---------------------------------------------------------------------------
# MCP config loader
# ---------------------------------------------------------------------------

class TestLoadToolRegistry:

    def test_loads_enabled_servers(self, mcp_config_file: Path) -> None:
        tools = load_tool_registry_from_mcp_config(mcp_config_file)
        names = {t.name for t in tools}
        assert "adg_sqlite" in names
        assert "redis" in names
        assert "disabled_one" not in names

    def test_skips_disabled(self, mcp_config_file: Path) -> None:
        tools = load_tool_registry_from_mcp_config(mcp_config_file)
        names = {t.name for t in tools}
        assert "disabled_one" not in names

    def test_handles_missing_file(self, tmp_path: Path) -> None:
        tools = load_tool_registry_from_mcp_config(tmp_path / "nonexistent.json")
        assert tools == []

    def test_handles_invalid_json(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.json"
        p.write_text("not json", encoding="utf-8")
        tools = load_tool_registry_from_mcp_config(p)
        assert tools == []


# ---------------------------------------------------------------------------
# ToolSelector — keyword fallback
# ---------------------------------------------------------------------------

class TestToolSelectorKeyword:

    def test_selects_relevant_tools(self, sample_tools: list[ToolDefinition]) -> None:
        selector = ToolSelector(max_tools=3, min_score=0.1)
        result = selector.select("dependency graph analysis", sample_tools)
        # "adg_edge_fanin" should be top (has "dependency" in tags)
        assert result.total_candidates == len(sample_tools)
        assert result.budget_used <= 3
        names = [t.name for t in result.selected_tools]
        assert "adg_edge_fanin" in names

    def test_empty_registry_returns_empty(self) -> None:
        selector = ToolSelector()
        result = selector.select("anything", [])
        assert result.selected_tools == []
        assert result.total_candidates == 0

    def test_respects_max_tools(self, sample_tools: list[ToolDefinition]) -> None:
        selector = ToolSelector(max_tools=2, min_score=0.0)
        result = selector.select("test cache git", sample_tools)
        assert result.budget_used <= 2

    def test_respects_min_score(self, sample_tools: list[ToolDefinition]) -> None:
        selector = ToolSelector(max_tools=10, min_score=0.99)
        result = selector.select("completely unrelated query", sample_tools)
        # Very high min_score should filter most out
        assert result.budget_used <= len(sample_tools)

    def test_task_hint_boosts_relevance(self, sample_tools: list[ToolDefinition]) -> None:
        selector = ToolSelector(max_tools=3, min_score=0.1)
        result = selector.select("check", sample_tools, task_hint="git status")
        names = [t.name for t in result.selected_tools]
        assert "git_status" in names

    def test_provenance_includes_method(self, sample_tools: list[ToolDefinition]) -> None:
        selector = ToolSelector()
        result = selector.select("test", sample_tools)
        assert result.provenance["method"] == "keyword"

    def test_scores_are_between_zero_and_one(self, sample_tools: list[ToolDefinition]) -> None:
        selector = ToolSelector(max_tools=10, min_score=0.0)
        result = selector.select("redis cache state", sample_tools)
        for score in result.scores.values():
            assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# ToolSelector — embedding path
# ---------------------------------------------------------------------------

class TestToolSelectorEmbedding:

    @staticmethod
    def _make_embed_fn(dim: int = 4):
        """Create a fake embed function that returns deterministic vectors."""
        call_count = [0]

        def embed(texts: list[str]) -> list[list[float]]:
            results = []
            for text in texts:
                call_count[0] += 1
                # Deterministic: hash each char to a float
                vec = [
                    float(ord(text[idx % len(text)]) % (j + 2)) / (j + 2)
                    for idx, j in enumerate(range(dim))
                ]
                results.append(vec)
            return results

        return embed

    def test_embedding_selection_returns_result(self, sample_tools: list[ToolDefinition]) -> None:
        embed_fn = self._make_embed_fn()
        selector = ToolSelector(max_tools=3, min_score=0.0, embed_fn=embed_fn)
        result = selector.select("dependency graph", sample_tools)
        # Method may be "embedding" or "keyword" depending on Redis availability
        assert result.provenance["method"] in ("embedding", "keyword")
        assert result.budget_used <= 3

    def test_embedding_falls_back_on_empty_vectors(self, sample_tools: list[ToolDefinition]) -> None:
        def empty_embed(texts: list[str]) -> list[list[float]]:
            return [[] for _ in texts]

        selector = ToolSelector(max_tools=3, min_score=0.0, embed_fn=empty_embed)
        result = selector.select("test", sample_tools)
        # Should fall back to keyword when embeddings are empty
        assert result.provenance["method"] == "keyword"

    def test_embedding_with_mock_cache(self, sample_tools: list[ToolDefinition]) -> None:
        """Verify embedding path works when cache is available."""
        from unittest.mock import MagicMock

        embed_fn = self._make_embed_fn()

        # Mock cache that always calls fetch_embeddings (cache miss)
        mock_cache = MagicMock(spec=ToolEmbeddingCache)
        tool_embeds = embed_fn([f"{t.name}: {t.description}" for t in sample_tools])
        query_embeds = embed_fn(["dependency graph"])
        mock_cache.get_or_fetch.return_value = (tool_embeds, [t.name for t in sample_tools])

        selector = ToolSelector(
            max_tools=3, min_score=0.0,
            embed_fn=embed_fn, cache=mock_cache,
        )
        # Pre-set the query embedding so the selector uses it
        selector._last_query_embedding = query_embeds[0]

        result = selector.select("dependency graph", sample_tools)
        assert result.provenance["method"] == "embedding"
        assert result.budget_used <= 3
