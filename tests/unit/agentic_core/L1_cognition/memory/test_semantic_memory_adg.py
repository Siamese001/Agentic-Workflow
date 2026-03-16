"""ADG-driven tests for L1_cognition/memory/SemanticMemory.py — fan_in=1."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_semantic_memory_adg")
_emit_applies_guardrail("p0", "test_semantic_memory_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_semantic_memory_adg", "policy_binding")
_emit_snapshots_state("p0", "test_semantic_memory_adg", "state_snapshot")
emit_replay_key("p0", "test_semantic_memory_adg")
emit_determinism_digest("p0", "test_semantic_memory_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.memory.SemanticMemory import (
    EmbeddingProvider,
    SemanticMemory,
    VectorIndex,
)


class TestEmbeddingProvider:
    def test_creates_with_default(self):
        ep = EmbeddingProvider()
        assert ep.model == "default"

    def test_embed_returns_list(self):
        ep = EmbeddingProvider()
        result = ep.embed("hello world")
        assert isinstance(result, list)
        assert len(result) == 384


class TestVectorIndex:
    def test_creates(self):
        idx = VectorIndex()
        assert idx.dimension == 384

    def test_add_and_search(self):
        idx = VectorIndex()
        idx.add("key1", [0.1] * 384)
        results = idx.search([0.0] * 384, top_k=5)
        assert "key1" in results

    def test_search_respects_top_k(self):
        idx = VectorIndex()
        for i in range(10):
            idx.add(f"k{i}", [float(i)] * 384)
        results = idx.search([0.0] * 384, top_k=3)
        assert len(results) <= 3


class TestSemanticMemory:
    def test_creates(self):
        mem = SemanticMemory()
        assert mem is not None

    def test_store_and_retrieve(self):
        mem = SemanticMemory()
        mem.store("concept", "AI is cool")
        val = mem.retrieve("concept")
        assert val == "AI is cool"

    def test_retrieve_missing_returns_none(self):
        mem = SemanticMemory()
        assert mem.retrieve("nonexistent") is None
