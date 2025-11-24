"""Test basic vector search functionality."""
import pytest
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


@patch('l2.vector_search_executor.OpenAI')
@patch('l2.vector_search_executor.PineconeClient')
def test_vector_search_flow(mock_pinecone_client, mock_openai):
    """Test the complete vector search flow with mocks."""
    # Setup mocks
    mock_client = MagicMock()
    mock_pinecone_client.return_value = mock_client
    
    mock_embedding = [0.1, 0.2, 0.3]
    mock_openai.return_value.embeddings.create.return_value.data = [
        MagicMock(embedding=mock_embedding)
    ]
    
    # Import after setting up mocks to avoid actual API calls
    from l2.vector_search_executor import VectorSearchExecutor
    
    # Initialize executor
    executor = VectorSearchExecutor(mock_client)
    
    # Test get_embedding
    embedding = executor.get_embedding("test")
    assert embedding == mock_embedding
    mock_openai.return_value.embeddings.create.assert_called_once_with(
        input="test",
        model="text-embedding-3-small"
    )
    
    # Reset mock for next test
    mock_openai.return_value.embeddings.create.reset_mock()
    
    # Test upsert_text
    executor.upsert_text("test-ns", "doc1", "test content", {"category": "test"})
    mock_client.upsert.assert_called_once()
    
    # Test search
    mock_client.query.return_value = [
        {"id": "doc1", "score": 0.95, "metadata": {"text": "test content"}}
    ]
    results = executor.search("test-ns", "test query", 1)
    assert len(results) == 1
    assert results[0].id == "doc1"
    assert results[0].score == 0.95
    assert results[0].metadata["text"] == "test content"
