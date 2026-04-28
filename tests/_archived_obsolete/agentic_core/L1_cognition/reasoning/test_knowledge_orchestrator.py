"""
Tests for KnowledgeOrchestrator - knowledge retrieval and orchestration logic.

Coverage:
- Knowledge source registration
- Query routing to appropriate sources
- Knowledge fusion from multiple sources
- Caching behavior
- Error handling for failed retrievals
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from agentic_core.L1_cognition.reasoning.knowledge_orchestrator import KnowledgeOrchestrator


class TestKnowledgeOrchestrator:
    """Test suite for KnowledgeOrchestrator."""

    def test_init_with_empty_sources(self):
        """Test initialization with no knowledge sources."""
        orchestrator = KnowledgeOrchestrator()
        assert len(orchestrator.sources) == 0

    def test_register_knowledge_source(self):
        """Test registering a knowledge source."""
        orchestrator = KnowledgeOrchestrator()
        source = Mock()
        source.name = "test_source"
        
        orchestrator.register_source(source)
        assert "test_source" in orchestrator.sources

    def test_register_duplicate_source_raises_error(self):
        """Test registering duplicate source raises error."""
        orchestrator = KnowledgeOrchestrator()
        source = Mock()
        source.name = "test_source"
        
        orchestrator.register_source(source)
        
        with pytest.raises(ValueError):
            orchestrator.register_source(source)

    def test_route_query_to_single_source(self):
        """Test routing query to appropriate source."""
        orchestrator = KnowledgeOrchestrator()
        source = Mock()
        source.name = "codebase"
        source.can_handle.return_value = True
        source.query.return_value = ["result1", "result2"]
        
        orchestrator.register_source(source)
        results = orchestrator.query("test query")
        
        assert len(results) == 2
        source.can_handle.assert_called_once_with("test query")
        source.query.assert_called_once_with("test query")

    def test_route_query_to_multiple_sources(self):
        """Test routing query to multiple capable sources."""
        orchestrator = KnowledgeOrchestrator()
        source1 = Mock()
        source1.name = "source1"
        source1.can_handle.return_value = True
        source1.query.return_value = ["result1"]
        
        source2 = Mock()
        source2.name = "source2"
        source2.can_handle.return_value = True
        source2.query.return_value = ["result2"]
        
        orchestrator.register_source(source1)
        orchestrator.register_source(source2)
        
        results = orchestrator.query("test query", fuse_results=True)
        
        assert len(results) >= 2  # Both sources contribute

    def test_fuse_knowledge_results(self):
        """Test knowledge fusion from multiple sources."""
        orchestrator = KnowledgeOrchestrator()
        
        results1 = [{"content": "A", "confidence": 0.9}]
        results2 = [{"content": "B", "confidence": 0.8}]
        
        fused = orchestrator.fuse_results([results1, results2])
        
        assert len(fused) == 2
        # Results should be ranked by confidence
        assert fused[0]["confidence"] >= fused[1]["confidence"]

    def test_cache_query_results(self):
        """Test caching of query results."""
        orchestrator = KnowledgeOrchestrator(cache_enabled=True)
        source = Mock()
        source.name = "test_source"
        source.can_handle.return_value = True
        source.query.return_value = ["result"]
        
        orchestrator.register_source(source)
        
        # First call
        results1 = orchestrator.query("test query")
        source.query.assert_called_once()
        
        # Second call should use cache
        results2 = orchestrator.query("test query")
        assert source.query.call_count == 1  # Not called again

    def test_invalidate_cache(self):
        """Test cache invalidation."""
        orchestrator = KnowledgeOrchestrator(cache_enabled=True)
        source = Mock()
        source.name = "test_source"
        source.can_handle.return_value = True
        source.query.return_value = ["result"]
        
        orchestrator.register_source(source)
        orchestrator.query("test query")
        
        orchestrator.invalidate_cache()
        orchestrator.query("test query")
        
        # Should call query again after invalidation
        assert source.query.call_count == 2

    def test_handle_source_failure(self):
        """Test graceful handling of source failure."""
        orchestrator = KnowledgeOrchestrator()
        source = Mock()
        source.name = "failing_source"
        source.can_handle.return_value = True
        source.query.side_effect = Exception("Source failed")
        
        orchestrator.register_source(source)
        
        # Should not crash, return empty or partial results
        results = orchestrator.query("test query")
        assert isinstance(results, list)

    def test_unregister_source(self):
        """Test unregistering a knowledge source."""
        orchestrator = KnowledgeOrchestrator()
        source = Mock()
        source.name = "test_source"
        
        orchestrator.register_source(source)
        assert "test_source" in orchestrator.sources
        
        orchestrator.unregister_source("test_source")
        assert "test_source" not in orchestrator.sources

    def test_get_source_status(self):
        """Test retrieving status of all sources."""
        orchestrator = KnowledgeOrchestrator()
        source = Mock()
        source.name = "test_source"
        source.is_healthy.return_value = True
        
        orchestrator.register_source(source)
        status = orchestrator.get_source_status()
        
        assert "test_source" in status
        assert status["test_source"]["healthy"] is True
