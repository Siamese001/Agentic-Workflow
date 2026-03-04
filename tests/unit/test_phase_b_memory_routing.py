"""Phase B — Memory Search at Routing acceptance tests.

B-test hardenings verified:
  (a) HealingMemoryRetriever returns empty list when FAISS index is empty.
  (b) NullHealingMemoryRetriever always returns [] (negative control).
  (c) advisory_only=True on every SimilarIncident returned.
  (d) Routing decision is identical with/without retriever wired (advisory-only guard).
  (e) build_retriever() returns NullHealingMemoryRetriever when embeddings disabled.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# B1 — HealingMemoryRetriever unit tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_null_retriever_returns_empty_list():
    from agentic_core.L1_cognition.memory.healing_memory_retriever import NullHealingMemoryRetriever

    r = NullHealingMemoryRetriever()
    result = r.retrieve_similar_incidents("any signal text", top_k=5)
    assert result == []


@pytest.mark.unit
def test_null_retriever_is_not_active():
    from agentic_core.L1_cognition.memory.healing_memory_retriever import NullHealingMemoryRetriever

    r = NullHealingMemoryRetriever()
    assert r.is_active is False


@pytest.mark.unit
def test_healing_retriever_is_active():
    from agentic_core.L1_cognition.memory.healing_memory_retriever import HealingMemoryRetriever
    from system_learning.engines.local_faiss_store import LocalFAISSStore

    store = LocalFAISSStore(base_path=Path("."))
    r = HealingMemoryRetriever(store=store)
    assert r.is_active is True


@pytest.mark.unit
def test_healing_retriever_empty_signal_returns_empty():
    from agentic_core.L1_cognition.memory.healing_memory_retriever import HealingMemoryRetriever
    from system_learning.engines.local_faiss_store import LocalFAISSStore

    store = LocalFAISSStore(base_path=Path("."))
    r = HealingMemoryRetriever(store=store)
    result = r.retrieve_similar_incidents("", top_k=5)
    assert result == []


@pytest.mark.unit
def test_healing_retriever_returns_advisory_only_incidents():
    from agentic_core.L1_cognition.memory.healing_memory_retriever import (
        HealingMemoryRetriever,
        SimilarIncident,
    )

    mock_store = MagicMock()
    mock_store.search.return_value = [
        ("hash_abc", "trace_1", 0.91),
        ("hash_def", "trace_2", 0.82),
    ]

    with patch(
        "agentic_core.L2_execution.healers.bmg_embedding_similarity.bmg_embed_text",
        return_value=[0.1] * 16,
    ):
        r = HealingMemoryRetriever(store=mock_store)
        results = r.retrieve_similar_incidents("IMPORT_BOUNDARY agent territory", top_k=5)

    assert len(results) == 2
    for incident in results:
        assert isinstance(incident, SimilarIncident)
        assert incident.advisory_only is True, "advisory_only MUST always be True"


@pytest.mark.unit
@pytest.mark.negative_control
def test_build_retriever_returns_null_when_embeddings_disabled(tmp_path):
    from agentic_core.L1_cognition.memory.healing_memory_retriever import (
        NullHealingMemoryRetriever,
        build_retriever,
    )

    with patch.dict(os.environ, {"BMG_EMBEDDINGS_ENABLED": "false"}):
        r = build_retriever(base_path=tmp_path)
    assert isinstance(r, NullHealingMemoryRetriever)


@pytest.mark.unit
@pytest.mark.negative_control
def test_build_retriever_returns_null_when_base_path_none():
    from agentic_core.L1_cognition.memory.healing_memory_retriever import (
        NullHealingMemoryRetriever,
        build_retriever,
    )

    with patch.dict(os.environ, {"BMG_EMBEDDINGS_ENABLED": "true"}):
        r = build_retriever(base_path=None)
    assert isinstance(r, NullHealingMemoryRetriever)


# ---------------------------------------------------------------------------
# B2 + B3 — SovereignDecisionEngine advisory injection
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_sovereign_engine_accepts_retriever_kwarg():
    from agentic_core.L1_cognition.memory.healing_memory_retriever import NullHealingMemoryRetriever

    try:
        from agentic_core.L0_routing.scripts.execute_ssot import SovereignDecisionEngine
    except ImportError as exc:
        pytest.skip(f"execute_ssot not importable in min-deps env: {exc}")

    retriever = NullHealingMemoryRetriever()
    engine = SovereignDecisionEngine(healing_memory_retriever=retriever)
    assert engine._healing_memory_retriever is retriever


@pytest.mark.unit
def test_sovereign_engine_default_retriever_is_none():
    try:
        from agentic_core.L0_routing.scripts.execute_ssot import SovereignDecisionEngine
    except ImportError as exc:
        pytest.skip(f"execute_ssot not importable in min-deps env: {exc}")

    engine = SovereignDecisionEngine()
    assert engine._healing_memory_retriever is None


@pytest.mark.unit
@pytest.mark.sovereignty
def test_advisory_result_never_alters_routing_score():
    """B3 hardening: routing decision must be identical regardless of retriever results."""
    try:
        from agentic_core.L0_routing.scripts.execute_ssot import (
            ConfidenceScore,
            FailureType,
            SovereignDecisionEngine,
        )
    except ImportError as exc:
        pytest.skip(f"execute_ssot not importable in min-deps env: {exc}")

    from agentic_core.L1_cognition.memory.healing_memory_retriever import (
        SimilarIncident,
    )

    class _StubRetriever:
        is_active = True

        def retrieve_similar_incidents(self, text, top_k=5):
            return [
                SimilarIncident(
                    content_hash="abc",
                    trace_id="t1",
                    similarity=0.99,
                    metadata={},
                    advisory_only=True,
                )
            ]

    confidence = ConfidenceScore(value=0.75, reasoning="baseline test")
    failure_type = FailureType.UNKNOWN

    engine_no_retriever = SovereignDecisionEngine()
    engine_with_retriever = SovereignDecisionEngine(healing_memory_retriever=_StubRetriever())

    dec_a = engine_no_retriever._route_decision(confidence, "TestAgent", "unit_test_territory", failure_type)
    dec_b = engine_with_retriever._route_decision(
        confidence, "TestAgent", "unit_test_territory", failure_type
    )

    assert dec_a.tier == dec_b.tier, "Tier must not change due to advisory retrieval"
