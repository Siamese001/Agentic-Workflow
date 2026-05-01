"""
Unit tests for HOP2ResearchAgent (V2).
Verifies Vector-First strategy, RAG fallback, and V2 architecture compliance.
"""

from unittest.mock import MagicMock

import pytest
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

from apps_lic.engines.HOP2ResearchAgent import HOP2ResearchAgent

# --- Fixtures ---


@pytest.fixture
def mock_memory_store():
    """Mock VectorMemoryStore with async query methods."""
    store = MagicMock()
    # Mocking standard responses with sufficient content to pass critique
    store.query_by_company.return_value = [
        {
            "text": "Company Context A - detailed information about strategic priorities and initiatives for 2025",
            "metadata": {"source_weight": 0.8, "age_days": 10},
        },
        {
            "text": "Company Context B - additional context about roadmap and platform",
            "metadata": {"source_weight": 0.7, "age_days": 15},
        },
        {
            "text": "Company Context C - more strategic information",
            "metadata": {"source_weight": 0.75, "age_days": 20},
        },
    ]
    store.query_by_executive.return_value = [
        {
            "text": "Executive Context A - recent LinkedIn posts and presentations about leadership vision",
            "metadata": {"source_weight": 0.9, "age_days": 5},
        },
        {
            "text": "Executive Context B - background and career history with detailed achievements",
            "metadata": {"source_weight": 0.85, "age_days": 10},
        },
    ]
    store.get_strategic_briefs.return_value = [
        {
            "text": "Strategic Brief - Comprehensive analysis of company direction, key initiatives, market positioning, competitive landscape, and growth strategy for the upcoming fiscal year with detailed roadmap and milestones",
            "metadata": {"source_weight": 1.0, "age_days": 5},
        }
    ]
    return store


@pytest.fixture
def mock_search_client():
    """Mock Search Client for RAG."""
    client = MagicMock()
    client.search = MagicMock(
        return_value=[{"snippet": "New News Article", "link": "http://news.com", "title": "News"}]
    )
    return client


@pytest.fixture
def resources():
    """V2 State Resources."""
    return ImmutableStagingBuffer(), TraceRegistry()


@pytest.fixture
def input_data():
    """Standard HOP-1 Input Data."""
    return {
        "recipient_company": "Acme Corp",
        "recipient_name": "Wile E. Coyote",
        "Archetype": "C_LEVEL",
    }


# --- Tests ---


class TestHOP2FastPath:
    """Verifies the Vector-First (Fast Path) logic."""

    def test_cache_hit_execution(self, mock_memory_store, resources, input_data):
        """
        Scenario: Vector store returns high-quality, recent data.
        Expected: Agent relies on cache, writes output, traces CACHE_HIT.
        """
        buffer, registry = resources
        buffer.write_once("hop1_analysis", input_data)

        # Setup Agent
        agent = HOP2ResearchAgent(memory_store=mock_memory_store)

        # Execute
        agent.run_phase(buffer, registry)

        # 1. Verify Output
        result = buffer.read("hop2_research")
        assert result is not None
        assert result["cache_hit"] is True
        assert result["fallback_used"] is False
        assert len(result["strategic_brief"]) > 0

        # 2. Verify Traces
        traces = [t["type"] for t in registry.get_traces()]
        assert "PHASE_START" in traces
        assert "VECTOR_RESULTS" in traces
        assert "DECISION_CACHE_HIT" in traces
        assert "RAG_ACTIVATED" not in traces  # Should NOT trigger RAG
        assert "DECISION_FINAL" in traces

    def test_missing_input_failure(self, mock_memory_store, resources):
        """
        Scenario: Buffer missing 'hop1_analysis'.
        Expected: RuntimeError (raised by LICAgentBase) wrapping ValueError.
        """
        buffer, registry = resources
        # Do NOT write input

        agent = HOP2ResearchAgent(memory_store=mock_memory_store)

        with pytest.raises(RuntimeError) as exc:
            agent.run_phase(buffer, registry)

        assert "execution failed" in str(exc.value)

        # Check trace for specific data error
        traces = registry.get_traces()
        error_trace = next(t for t in traces if t["type"] == "DATA_ERROR")
        assert "Missing 'hop1_analysis'" in error_trace["details"]["msg"]


class TestHOP2SlowPath:
    """Verifies the RAG Fallback (Slow Path) logic."""

    def test_cache_miss_rag_activation(
        self, mock_memory_store, mock_search_client, resources, input_data
    ):
        """
        Scenario: Vector store missing strategic brief (gap).
        Expected: Agent detects gap, triggers RAG, merges results.
        """
        buffer, registry = resources
        buffer.write_once("hop1_analysis", input_data)

        # Cripple the vector store to force a gap
        mock_memory_store.get_strategic_briefs.return_value = []  # Missing brief

        agent = HOP2ResearchAgent(memory_store=mock_memory_store, search_client=mock_search_client)

        # Execute
        agent.run_phase(buffer, registry)

        # 1. Verify Output
        result = buffer.read("hop2_research")
        assert result["cache_hit"] is False
        assert result["fallback_used"] is True
        assert "strategic_brief" in result["gaps_identified"]

        # Verify RAG results merged in
        # (Mock search returns "New News Article", logic formats it)
        # rag_results contains both original vector store results and new RAG results
        # Only RAG results will have "SourceType" key
        rag_texts = [
            r["text"]
            for r in result["rag_results"]
            if r.get("metadata", {}).get("SourceType") == "STRATEGIC_BRIEF"
        ]
        assert any("New News Article" in t for t in rag_texts)

        # 2. Verify Traces
        traces = registry.get_traces()
        types = [t["type"] for t in traces]
        assert "DECISION_CACHE_MISS" in types
        assert "RAG_ACTIVATED" in types

    def test_rag_skipped_if_no_client(self, mock_memory_store, resources, input_data):
        """
        Scenario: Gaps detected but NO search client provided.
        Expected: Agent traces RAG_SKIPPED and returns partial data.
        """
        buffer, registry = resources
        buffer.write_once("hop1_analysis", input_data)

        # Cripple vector store
        mock_memory_store.get_strategic_briefs.return_value = []

        # Initialize WITHOUT search_client
        agent = HOP2ResearchAgent(memory_store=mock_memory_store, search_client=None)

        agent.run_phase(buffer, registry)

        # Verify Traces
        traces = registry.get_traces()
        types = [t["type"] for t in traces]
        assert "RAG_SKIPPED" in types
        assert "RAG_ACTIVATED" not in types
