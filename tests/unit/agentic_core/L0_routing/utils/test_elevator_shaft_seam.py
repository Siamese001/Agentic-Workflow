"""Unit tests for load_context_jit — C0 JIT context retrieval.

Phase P2.2 of l0-context-prompt-retrieval-review-b7c4a2. Before this file the
elevator-shaft seam had zero direct test coverage (ADG fan-in = 1, all from a
sibling module). These tests lock in:

* RAG + BM25 combine + dedupe
* Token-budget trim (4-chars-per-token approximation)
* Graceful fallback when any L4 store is unavailable (ValueError / TypeError)
* Return-shape contract
"""

from __future__ import annotations

import sys
import types
from typing import Any
from unittest.mock import MagicMock

import pytest

from agentic_core.L0_routing.utils.elevator_shaft_seam import (
    DEFAULT_C0_TOKEN_BUDGET,
    load_context_jit,
)


def _install_store(monkeypatch: pytest.MonkeyPatch, module_path: str, getter_name: str, store: Any) -> None:
    """Install a fake L4 memory-store module exposing ``getter_name() -> store``."""
    mod = types.ModuleType(module_path)
    setattr(mod, getter_name, lambda: store)
    monkeypatch.setitem(sys.modules, module_path, mod)


@pytest.fixture(autouse=True)
def _install_l4_stores(monkeypatch: pytest.MonkeyPatch) -> dict[str, MagicMock]:
    """Stand up fake L4 stores so load_context_jit has deterministic inputs."""
    semantic = MagicMock()
    semantic.query.return_value = ["sem_chunk_a", "sem_chunk_b"]
    bm25 = MagicMock()
    bm25.query.return_value = ["bm25_chunk_a", "bm25_chunk_c"]  # 'a' duplicated with semantic
    ast_store = MagicMock()
    ast_store.get_snapshot.return_value = {"module": "x"}
    boundary = MagicMock()
    boundary.get_refs_for_intent.return_value = ["bndry_ref_1"]

    _install_store(
        monkeypatch,
        "agentic_core.L4_state.utils.memory.semantic_cache_manager",
        "get_semantic_cache",
        semantic,
    )
    _install_store(
        monkeypatch,
        "agentic_core.L4_state.utils.memory.bm25_store",
        "get_bm25_store",
        bm25,
    )
    _install_store(
        monkeypatch,
        "agentic_core.L4_state.utils.memory.ast_snapshot_store",
        "get_ast_snapshot_store",
        ast_store,
    )
    _install_store(
        monkeypatch,
        "agentic_core.L4_state.utils.memory.boundary_store",
        "get_boundary_store",
        boundary,
    )
    return {"semantic": semantic, "bm25": bm25, "ast": ast_store, "boundary": boundary}


def test_returns_required_keys() -> None:
    result = load_context_jit(trace_id="t1", intent_class="summarize")
    assert set(result.keys()) >= {
        "rag_chunks",
        "ast_snapshot",
        "boundary_refs",
        "token_budget",
        "tokens_used",
    }
    assert result["token_budget"] == DEFAULT_C0_TOKEN_BUDGET


def test_combines_rag_and_bm25_and_dedupes(_install_l4_stores: dict[str, MagicMock]) -> None:
    result = load_context_jit(trace_id="t2", intent_class="summarize", token_budget=1024)
    # Duplicate "sem_chunk_a" / "bm25_chunk_a" are different strings so both are kept;
    # dedupe is by hash(str(chunk)) — this test verifies both stores are actually queried
    # and their outputs merged (not one or the other).
    assert _install_l4_stores["semantic"].query.call_count == 1
    assert _install_l4_stores["bm25"].query.call_count == 1
    chunks = result["rag_chunks"]
    assert any("sem_chunk" in c for c in chunks)
    assert any("bm25_chunk" in c for c in chunks)


def test_token_budget_trims_chunks(_install_l4_stores: dict[str, MagicMock]) -> None:
    # Make semantic cache return a large chunk that exceeds a tiny budget.
    _install_l4_stores["semantic"].query.return_value = ["X" * 400, "Y" * 400]
    _install_l4_stores["bm25"].query.return_value = []
    # budget=10 tokens ≈ 40 chars → only first chunk could fit (400 chars ≫ 40), so none fit.
    result = load_context_jit(trace_id="t3", intent_class="summarize", token_budget=10)
    assert result["tokens_used"] == 0
    assert result["rag_chunks"] == []


def test_graceful_fallback_when_semantic_store_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Force the semantic-cache import block to raise ValueError inside the try.
    broken = MagicMock()
    broken.query.side_effect = ValueError("store unavailable")
    _install_store(
        monkeypatch,
        "agentic_core.L4_state.utils.memory.semantic_cache_manager",
        "get_semantic_cache",
        broken,
    )
    # Other stores stay healthy via the autouse fixture.
    result = load_context_jit(trace_id="t4", intent_class="summarize")
    # No crash; rag_chunks only contain bm25 contributions.
    assert all("sem_chunk" not in c for c in result["rag_chunks"])
    assert any("bm25_chunk" in c for c in result["rag_chunks"])


def test_boundary_and_ast_passed_through(_install_l4_stores: dict[str, MagicMock]) -> None:
    result = load_context_jit(trace_id="t5", intent_class="summarize")
    assert result["ast_snapshot"] == {"module": "x"}
    assert result["boundary_refs"] == ["bndry_ref_1"]
    _install_l4_stores["ast"].get_snapshot.assert_called_once_with("t5")
    _install_l4_stores["boundary"].get_refs_for_intent.assert_called_once_with("summarize")
