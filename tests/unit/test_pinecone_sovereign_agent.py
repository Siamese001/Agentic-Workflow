import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import numpy as np
from agentic_core.L4_state.vector.pinecone_sovereign_agent import PineconeSovereignAgent

@pytest.fixture
def mock_index():
    """A sovereign mock of a Pinecone index."""
    idx = MagicMock()
    # Mocking a standard semantic search result
    idx.query.return_value = {
        "matches": [
            {"id": "file_1", "score": 0.92, "metadata": {"territory": "agentic_core/L3_orchestration"}}
        ]
    }
    idx.describe_index_stats.return_value = {"total_vector_count": 42, "index_fullness": 0.01}
    return idx

@pytest.fixture
def agent(tmp_path, mock_index):
    """The Agent Proof-Out."""
    with patch("agentic_core.L4_state.vector.pinecone_sovereign_agent.Pinecone") as mock_pc:
        mock_pc.return_value.Index.return_value = mock_index
        # Mocking the embedding engine to return a fixed-size 'thought'
        with patch("agentic_core.L4_state.vector.pinecone_sovereign_agent.SubAtomicEngine") as mock_engine:
            mock_engine.return_value.resilient_mutation.return_value = {"embedding": [0.1] * 1536}
            agent_instance = PineconeSovereignAgent(tmp_path)
            return agent_instance, mock_index

def test_embedding_repair_logic(agent):
    agent_instance, _ = agent
    
    # CASE: The vector is too short.
    broken_emb = [0.1] * 100
    repaired = agent_instance._validate_and_repair_embedding(broken_emb, "test_file")
    
    # VERDICT: It must be padded back to 1536 dimensions.
    assert len(repaired) == 1536
    assert repaired[1535] == 0.0 # Padded with zeros
    print("   [OK] Embedding repair logic verified.")

def test_ghost_purge(agent):
    agent_instance, mock_idx = agent
    file_path = Path("agentic_core/L2_state/old_ledger.py")
    
    agent_instance.purge_ghost_vector(file_path)
    
    # VERDICT: The delete call must use the canonical ID format.
    expected_id = "file_agentic_core_L2_state_old_ledger.py"
    mock_idx.delete.assert_called_with(ids=[expected_id])

def test_semantic_search(agent):
    agent_instance, mock_idx = agent
    query_text = "test query for semantic search"
    
    results = agent_instance.semantic_search(query_text, top_k=5)
    
    # Verify query was called with embedding
    mock_idx.query.assert_called_once()
    call_args = mock_idx.query.call_args
    assert "vector" in call_args.kwargs
    assert call_args.kwargs["top_k"] == 5
    assert len(results["matches"]) == 1
    assert results["matches"][0]["score"] == 0.92

def test_bootstrap_territory_index(agent):
    agent_instance, mock_idx = agent
    
    # Mock the file system scan
    with patch.object(agent_instance, "_scan_and_index_territories") as mock_scan:
        agent_instance.bootstrap_territory_index()
        mock_scan.assert_called_once()

def test_index_health_check(agent):
    agent_instance, mock_idx = agent
    
    health = agent_instance.check_index_health()
    
    assert health["total_vectors"] == 42
    assert health["index_fullness"] == 0.01
    assert health["status"] == "healthy"

def test_vector_upsert(agent):
    agent_instance, mock_idx = agent
    file_path = Path("test_file.py")
    test_embedding = [0.1] * 1536
    metadata = {"territory": "test", "size": 100}
    
    agent_instance.upsert_vector(file_path, test_embedding, metadata)
    
    expected_id = "file_test_file.py"
    mock_idx.upsert.assert_called_once_with(
        vectors=[{
            "id": expected_id,
            "values": test_embedding,
            "metadata": metadata
        }]
    )

def test_batch_vector_operations(agent):
    agent_instance, mock_idx = agent
    vectors = [
        (Path("file1.py"), [0.1] * 1536, {"territory": "test"}),
        (Path("file2.py"), [0.2] * 1536, {"territory": "test"})
    ]
    
    agent_instance.batch_upsert(vectors)
    
    # Verify batch upsert was called
    mock_idx.upsert.assert_called_once()
    call_args = mock_idx.upsert.call_args
    assert len(call_args.kwargs["vectors"]) == 2

def test_error_handling_on_pinecone_failure(tmp_path):
    """Test graceful handling when Pinecone is unavailable."""
    with patch("agentic_core.L4_state.vector.pinecone_sovereign_agent.Pinecone") as mock_pc:
        mock_pc.return_value.Index.side_effect = Exception("Pinecone connection failed")
        
        with pytest.raises(Exception):
            PineconeSovereignAgent(Path("/tmp"))

def test_embedding_dimension_validation(agent):
    agent_instance, _ = agent
    
    # Test embedding that's too long
    long_emb = [0.1] * 2000
    repaired = agent_instance._validate_and_repair_embedding(long_emb, "test")
    
    # Should be truncated to 1536
    assert len(repaired) == 1536
    
    # Test correct size embedding
    correct_emb = [0.1] * 1536
    repaired = agent_instance._validate_and_repair_embedding(correct_emb, "test")
    
    # Should remain unchanged
    assert len(repaired) == 1536
    assert repaired == correct_emb
