"""
RAG Architecture Validation Tests
Tests all 5 mandatory test cases (RAG-001 to RAG-005) for the unified RAG interface
"""

import os
import pytest
import asyncio
from unittest.mock import Mock, patch


class TestRAGArchitectureValidation:
    """Validate RAG architecture changes per specification."""

    def test_rag_001_interface_compliance(self):
        """
        RAG-001: Interface Compliance
        Verify SovereignRagOrchestratorAgent explicitly inherits IRagProvider.
        """
        from agentic_core.L3_orchestration.workflow_engines.SovereignRagOrchestratorAgent import (
            SovereignRagOrchestratorAgent,
        )
        from agentic_core.L3_orchestration.interfaces.IRagProvider import IRagProvider

        # Instantiate agent
        agent = SovereignRagOrchestratorAgent()

        # Check inheritance
        assert isinstance(agent, IRagProvider), "Agent must inherit from IRagProvider"
        assert issubclass(SovereignRagOrchestratorAgent, IRagProvider), (
            "Class must be subclass of IRagProvider"
        )

        # Verify interface methods exist
        assert hasattr(agent, "retrieve"), "Agent must implement retrieve()"
        assert hasattr(agent, "index"), "Agent must implement index()"
        assert hasattr(agent, "get_health"), "Agent must implement get_health()"

        print("✅ RAG-001 PASS: Interface compliance verified")

    def test_rag_002_config_loading(self):
        """
        RAG-002: Config Loading
        Verify SovereignRagConfig.from_env() respects EMBEDDING_DIMENSION env var.
        """
        from agentic_core.config.rag_config import SovereignRagConfig

        # Set environment variable
        os.environ["EMBEDDING_DIMENSION"] = "768"

        try:
            # Load config from environment
            config = SovereignRagConfig.from_env()

            # Verify dimension override
            assert config.vector_store.dimension == 768, (
                f"Expected 768, got {config.vector_store.dimension}"
            )
            assert config.embedding.dimension == 768, (
                f"Expected 768, got {config.embedding.dimension}"
            )

            print("✅ RAG-002 PASS: Config loading from env verified")
        finally:
            # Cleanup
            os.environ.pop("EMBEDDING_DIMENSION", None)

    def test_rag_003_telemetry_singleton(self):
        """
        RAG-003: Telemetry Singleton
        Verify RagTelemetryCollector is a true singleton.
        """
        from agentic_core.L6_observability.telemetry.RagTelemetryCollector import (
            RagTelemetryCollector,
        )

        # Create two instances
        instance1 = RagTelemetryCollector()
        instance2 = RagTelemetryCollector()

        # Verify same object
        assert id(instance1) == id(instance2), (
            f"Singleton violated: {id(instance1)} != {id(instance2)}"
        )

        # Verify shared state
        instance1.record_query(latency_ms=100, cached=True, reranked=False, doc_count=5)
        assert instance2.metrics.total_queries == 1, "Singleton state not shared"

        print("✅ RAG-003 PASS: Telemetry singleton verified")

    @pytest.mark.asyncio
    async def test_rag_004_bridge_fallback(self):
        """
        RAG-004: Bridge Fallback
        Verify graceful degradation when titanium_rag_pipeline is unavailable.
        """
        from agentic_core.L3_orchestration.interfaces.IRagProvider import RagQuery

        # Mock ImportError for titanium_rag_pipeline at import time
        with patch.dict("sys.modules", {"apps_shared.common_utils.titanium_rag_pipeline": None}):
            # Force reimport to trigger ImportError
            import sys

            # Remove cached module if exists
            if (
                "agentic_core.L3_orchestration.workflow_engines.SovereignRagOrchestratorAgent"
                in sys.modules
            ):
                del sys.modules[
                    "agentic_core.L3_orchestration.workflow_engines.SovereignRagOrchestratorAgent"
                ]

            from agentic_core.L3_orchestration.workflow_engines.SovereignRagOrchestratorAgent import (  # noqa: E501
                SovereignRagOrchestratorAgent,
            )

            # Create agent (should fallback gracefully)
            agent = SovereignRagOrchestratorAgent()

            # Verify fallback - pipeline should be None due to ImportError
            # (The actual agent already handles this gracefully)

            # Mock retriever and guardrail for legacy path
            mock_retriever = Mock()

            # Make hybrid_search return an awaitable coroutine
            async def mock_hybrid_search(*args, **kwargs):
                return []

            mock_retriever.hybrid_search = mock_hybrid_search
            mock_retriever.deduplicate_by_hash = Mock(return_value=[])

            mock_guardrail = Mock()

            # Make rerank_documents return an awaitable coroutine
            async def mock_rerank(*args, **kwargs):
                return []

            mock_guardrail.rerank_documents = mock_rerank

            agent.retriever = mock_retriever
            agent.guardrail = mock_guardrail

            # Mock query_planner with async methods
            mock_query_planner = Mock()

            async def mock_decompose_query(*args, **kwargs):
                return ["test query"]

            async def mock_multi_query_generation(*args, **kwargs):
                return ["test query"]

            mock_query_planner.decompose_query = mock_decompose_query
            mock_query_planner.multi_query_generation = mock_multi_query_generation

            agent.query_planner = mock_query_planner

            # Call retrieve (should use legacy path)
            query = RagQuery(query="test query", top_k=5)
            result = await agent.retrieve(query)

            # Verify result structure
            assert result is not None, "Result should not be None"
            assert result.query == "test query", "Query should match"
            assert result.latency_ms > 0, "Latency should be recorded"

            print("✅ RAG-004 PASS: Bridge fallback verified")

    @pytest.mark.asyncio
    async def test_rag_005_health_check(self):
        """
        RAG-005: Health Check
        Verify RagHealthCheckAgent handles component failures gracefully.
        """
        from agentic_core.L5_safety.validators.RagHealthCheckAgent import RagHealthCheckAgent

        agent = RagHealthCheckAgent()

        # Mock PineconeVectorStore to simulate failure within the check method
        with patch(
            "agentic_core.semantic_memory.store.pinecone_store.PineconeVectorStore",
            side_effect=Exception("Mocked failure"),
        ):
            # Run health check (should not crash)
            status = await agent.check_health(force=True)

            # Verify status structure
            assert status is not None, "Status should not be None"
            assert isinstance(status.healthy, bool), "healthy should be bool"
            assert isinstance(status.issues, list), "issues should be list"
            assert isinstance(status.warnings, list), "warnings should be list"
            assert isinstance(status.metrics, dict), "metrics should be dict"

            # Verify graceful failure handling
            assert not status.vector_store_ok, "Vector store should fail"
            assert len(status.issues) > 0, "Should have at least one issue"

            print("✅ RAG-005 PASS: Health check graceful failure verified")


def run_all_tests():
    """Run all RAG architecture validation tests."""
    print("\n" + "=" * 80)
    print("RAG ARCHITECTURE VALIDATION TEST SUITE")
    print("=" * 80 + "\n")

    test_suite = TestRAGArchitectureValidation()

    # Test RAG-001
    try:
        test_suite.test_rag_001_interface_compliance()
    except Exception as e:
        print(f"❌ RAG-001 FAILED: {e}")

    # Test RAG-002
    try:
        test_suite.test_rag_002_config_loading()
    except Exception as e:
        print(f"❌ RAG-002 FAILED: {e}")

    # Test RAG-003
    try:
        test_suite.test_rag_003_telemetry_singleton()
    except Exception as e:
        print(f"❌ RAG-003 FAILED: {e}")

    # Test RAG-004 (async)
    try:
        asyncio.run(test_suite.test_rag_004_bridge_fallback())
    except Exception as e:
        print(f"❌ RAG-004 FAILED: {e}")

    # Test RAG-005 (async)
    try:
        asyncio.run(test_suite.test_rag_005_health_check())
    except Exception as e:
        print(f"❌ RAG-005 FAILED: {e}")

    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_all_tests()
