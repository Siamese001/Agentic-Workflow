"""Test basic vector search functionality."""
from unittest.mock import MagicMock, patch

from l1.vector_search_planning import plan_vector_search, plan_vector_upsert


def test_plan_vector_search():
    """Test creating a vector search plan."""
    # Test with minimal parameters
    plan = plan_vector_search("test query")
    assert plan.query_text == "test query"
    assert plan.namespace == "default"
    assert plan.top_k == 5
    assert plan.metadata_filters == {}
    
    # Test with custom parameters
    filters = {"category": "test"}
    plan = plan_vector_search("test query", "test-ns", 10, filters)
    assert plan.query_text == "test query"
    assert plan.namespace == "test-ns"
    assert plan.top_k == 10
    assert plan.metadata_filters == filters


def test_plan_vector_upsert():
    """Test creating a vector upsert plan."""
    # Test with minimal parameters
    plan = plan_vector_upsert("doc1", "test content")
    assert plan.id == "doc1"
    assert plan.text == "test content"
    assert plan.namespace == "default"
    assert plan.metadata == {}
    
    # Test with metadata
    metadata = {"category": "test", "source": "test-source"}
    plan = plan_vector_upsert("doc2", "more content", "test-ns", metadata)
    assert plan.id == "doc2"
    assert plan.text == "more content"
    assert plan.namespace == "test-ns"
    assert plan.metadata == metadata


def test_vector_search_flow():
    """Test the complete vector search flow with mocks.
    
    REFACTORED: L2 VectorSearchExecutor now uses L4 PineconeAdapter,
    so we mock at the adapter level instead of OpenAI directly.
    """
    from l2.vector_search_executor import VectorSearchExecutor, SearchResult
    from l4 import VectorQueryResult
    
    # Setup mock L4 adapter
    mock_adapter = MagicMock()
    
    # Mock query results
    mock_adapter.query_by_text.return_value = [
        VectorQueryResult(id="doc1", score=0.95, metadata={"text": "test content"})
    ]
    
    # Initialize executor with mock adapter
    executor = VectorSearchExecutor(mock_adapter)
    
    # Test execute_search
    results = executor.execute_search("test-ns", "test query", 1)
    assert len(results) == 1
    assert results[0].id == "doc1"
    assert results[0].score == 0.95
    assert results[0].metadata["text"] == "test content"
    mock_adapter.query_by_text.assert_called_once()
    
    # Reset mock for next test
    mock_adapter.reset_mock()
    
    # Test execute_upsert
    mock_adapter.upsert_text_records.return_value = ["doc_001"]
    ids = executor.execute_upsert("test-ns", ["test content"], "doc", [{"category": "test"}])
    assert ids == ["doc_001"]
    mock_adapter.upsert_text_records.assert_called_once()






