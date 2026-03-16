"""ADG-driven tests for L1_cognition/engines/semantic_manager.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_semantic_manager_adg")
_emit_applies_guardrail("p0", "test_semantic_manager_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_semantic_manager_adg", "policy_binding")
_emit_snapshots_state("p0", "test_semantic_manager_adg", "state_snapshot")
emit_replay_key("p0", "test_semantic_manager_adg")
emit_determinism_digest("p0", "test_semantic_manager_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.engines.semantic_manager import (
    EmbeddingProvider,
    VectorIndex,
)


class TestEmbeddingProvider:
    def test_creates_with_default(self):
        ep = EmbeddingProvider()
        assert ep.model == "BAAI/bge-m3"

    def test_embed_returns_list(self):
        ep = EmbeddingProvider()
        result = ep.embed("hello")
        assert isinstance(result, list)
        assert len(result) > 0


class TestVectorIndex:
    def test_creates(self):
        idx = VectorIndex()
        assert idx.dimension == 1024

    def test_add_and_contains(self):
        idx = VectorIndex()
        idx.add("key1", [0.1] * 1024)
        assert "key1" in idx._vectors
