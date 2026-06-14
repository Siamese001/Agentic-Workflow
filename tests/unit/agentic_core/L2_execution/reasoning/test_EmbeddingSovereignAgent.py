"""Unit tests for agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent.

Wave 6.1 (P2 untested-module coverage) — unified embedding gateway. The
network/provider paths (get_embedding, _get_*_embedding) require live SDKs and
are out of scope; this suite covers the pure/deterministic surface only:
singleton identity (__new__/reset_instance/get_embedding_gateway), the
content-hash helper, the in-memory _audit stats accounting + FIFO rotation,
EXPECTED_DIMENSIONS shape, and the not-yet-implemented heal() contract.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import (
    EmbeddingSovereignAgent,
    get_embedding_gateway,
)


@pytest.fixture()
def agent() -> EmbeddingSovereignAgent:
    EmbeddingSovereignAgent.reset_instance()
    a = EmbeddingSovereignAgent()
    yield a
    EmbeddingSovereignAgent.reset_instance()


class TestSingleton:
    def test_new_returns_same_instance(self, agent: EmbeddingSovereignAgent) -> None:
        assert EmbeddingSovereignAgent() is agent

    def test_gateway_helper_returns_singleton(self, agent: EmbeddingSovereignAgent) -> None:
        assert get_embedding_gateway() is agent

    def test_reset_instance_clears_singleton(self, agent: EmbeddingSovereignAgent) -> None:
        EmbeddingSovereignAgent.reset_instance()
        assert EmbeddingSovereignAgent() is not agent


class TestContentHash:
    def test_hash_is_deterministic(self, agent: EmbeddingSovereignAgent) -> None:
        assert agent._content_hash("hello") == agent._content_hash("hello")

    def test_hash_length_is_16(self, agent: EmbeddingSovereignAgent) -> None:
        assert len(agent._content_hash("anything")) == 16

    def test_hash_differs_by_content(self, agent: EmbeddingSovereignAgent) -> None:
        assert agent._content_hash("a") != agent._content_hash("b")


class TestExpectedDimensions:
    def test_dimensions_shape(self, agent: EmbeddingSovereignAgent) -> None:
        dims = agent.EXPECTED_DIMENSIONS
        assert set(dims.keys()) == {"gemini", "openai", "bge-m3"}
        assert dims["bge-m3"] == 1024
        assert all(isinstance(v, int) for v in dims.values())


class TestAuditAccounting:
    def test_cache_hit_increments_hits_and_total(self, agent: EmbeddingSovereignAgent) -> None:
        agent.operation_stats = {k: 0 for k in agent.operation_stats}
        agent._audit("openai", success=True, cached=True, latency_ms=1.0)
        assert agent.operation_stats["cache_hits"] == 1
        assert agent.operation_stats["cache_misses"] == 0
        assert agent.operation_stats["total"] == 1

    def test_cache_miss_success_increments_provider(self, agent: EmbeddingSovereignAgent) -> None:
        agent.operation_stats = {k: 0 for k in agent.operation_stats}
        agent._audit("openai", success=True, cached=False, latency_ms=2.0)
        assert agent.operation_stats["cache_misses"] == 1
        assert agent.operation_stats["openai"] == 1

    def test_cache_miss_failure_does_not_increment_provider(
        self, agent: EmbeddingSovereignAgent
    ) -> None:
        agent.operation_stats = {k: 0 for k in agent.operation_stats}
        agent._audit("gemini", success=False, cached=False, latency_ms=3.0)
        assert agent.operation_stats["cache_misses"] == 1
        assert agent.operation_stats["gemini"] == 0

    def test_audit_appends_log_entry(self, agent: EmbeddingSovereignAgent) -> None:
        before = len(agent.audit_log)
        agent._audit("bge-m3", success=True, cached=False, latency_ms=4.0)
        assert len(agent.audit_log) == before + 1
        entry = agent.audit_log[-1]
        assert entry["provider"] == "bge-m3"
        assert entry["cached"] is False
        assert "ts" in entry

    def test_audit_log_fifo_rotation(self, agent: EmbeddingSovereignAgent) -> None:
        limit = agent.config.max_audit_log_size
        # Fill to the limit, then add one more to trigger the 10% prune.
        agent.audit_log = []
        for _ in range(limit + 1):
            agent._audit("openai", success=True, cached=False, latency_ms=0.0)
        # After rotation the log must stay bounded (never grow unboundedly).
        assert len(agent.audit_log) <= limit


class TestHeal:
    def test_heal_returns_skipped_contract(self, agent: EmbeddingSovereignAgent) -> None:
        result = agent.heal({"type": "embedding_drift", "file": "x.py"})
        assert result["status"] == "skipped"
        assert result["artifacts"] == []
        assert result["errors"] == []
        assert "embedding_drift" in result["details"]

    def test_heal_handles_missing_type(self, agent: EmbeddingSovereignAgent) -> None:
        result = agent.heal({})
        assert result["status"] == "skipped"
        assert "unknown" in result["details"]
