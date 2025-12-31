import pytest
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from unittest.mock import MagicMock, patch
from pathlib import Path
import numpy as np
from agentic_core.L4_state.vector.pinecone_sovereign_agent import PineconeSovereignAgent

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


@pytest.fixture
def mock_index() -> Any:
    """A sovereign mock of a Pinecone index."""
    idx: Any = MagicMock()
    idx.query.return_value = {'matches': [{'id': 'file_1', 'score': 0.92, 'metadata': {'territory': 'agentic_core/L3_orchestration'}}]}
    idx.describe_index_stats.return_value = {'total_vector_count': 42, 'index_fullness': 0.01}
    return idx

@pytest.fixture
def agent(tmp_path: Any, mock_index: Any) -> Any:
    """The Agent Proof-Out."""
    with patch('agentic_core.L4_state.vector.pinecone_sovereign_agent.Pinecone') as mock_pc:
        mock_pc.return_value.Index.return_value = mock_index
        with patch('agentic_core.L4_state.vector.pinecone_sovereign_agent.SubAtomicEngine') as mock_engine:
            mock_engine.return_value.resilient_mutation.return_value = {'embedding': [0.1] * 1536}
            agent_instance: Any = PineconeSovereignAgent(tmp_path)
            return (agent_instance, mock_index)

def test_embedding_repair_logic(agent: Any) -> Any:
    """Brief description of functionality and purpose."""
    agent_instance, _ = agent
    broken_emb: Any = [0.1] * 100
    repaired: Any = agent_instance._validate_and_repair_embedding(broken_emb, 'test_file')
    assert len(repaired) == 1536
    assert repaired[1535] == 0.0
    print('   [OK] Embedding repair logic verified.')

def test_ghost_purge(agent: Any) -> Any:
    """Brief description of functionality and purpose."""
    agent_instance, mock_idx = agent
    file_path: Any = Path('agentic_core/L2_state/old_ledger.py')
    agent_instance.purge_ghost_vector(file_path)
    expected_id: Any = 'file_agentic_core_L2_state_old_ledger.py'
    mock_idx.delete.assert_called_with(ids=[expected_id])

def test_semantic_search(agent: Any) -> Any:
    """Brief description of functionality and purpose."""
    agent_instance, mock_idx = agent
    query_text: Any = 'test query for semantic search'
    results: Any = agent_instance.semantic_search(query_text, top_k=5)
    mock_idx.query.assert_called_once()
    call_args: Any = mock_idx.query.call_args
    assert 'vector' in call_args.kwargs
    assert call_args.kwargs['top_k'] == 5
    assert len(results['matches']) == 1
    assert results['matches'][0]['score'] == 0.92

def test_bootstrap_territory_index(agent: Any) -> Any:
    """Brief description of functionality and purpose."""
    agent_instance, mock_idx = agent
    with patch.object(agent_instance, '_scan_and_index_territories') as mock_scan:
        agent_instance.bootstrap_territory_index()
        mock_scan.assert_called_once()

def test_index_health_check(agent: Any) -> Any:
    """Brief description of functionality and purpose."""
    agent_instance, mock_idx = agent
    health: Any = agent_instance.check_index_health()
    assert health['total_vectors'] == 42
    assert health['index_fullness'] == 0.01
    assert health['status'] == 'healthy'

def test_vector_upsert(agent: Any) -> Any:
    """Brief description of functionality and purpose."""
    agent_instance, mock_idx = agent
    file_path: Any = Path('test_file.py')
    test_embedding: Any = [0.1] * 1536
    metadata: Any = {'territory': 'test', 'size': 100}
    agent_instance.upsert_vector(file_path, test_embedding, metadata)
    expected_id: Any = 'file_test_file.py'
    mock_idx.upsert.assert_called_once_with(vectors=[{'id': expected_id, 'values': test_embedding, 'metadata': metadata}])

def test_batch_vector_operations(agent: Any) -> Any:
    """Brief description of functionality and purpose."""
    agent_instance, mock_idx = agent
    vectors: Any = [(Path('file1.py'), [0.1] * 1536, {'territory': 'test'}), (Path('file2.py'), [0.2] * 1536, {'territory': 'test'})]
    agent_instance.batch_upsert(vectors)
    mock_idx.upsert.assert_called_once()
    call_args: Any = mock_idx.upsert.call_args
    assert len(call_args.kwargs['vectors']) == 2

def test_error_handling_on_pinecone_failure(tmp_path: Any) -> Any:
    """Test graceful handling when Pinecone is unavailable."""
    with patch('agentic_core.L4_state.vector.pinecone_sovereign_agent.Pinecone') as mock_pc:
        mock_pc.return_value.Index.side_effect = Exception('Pinecone connection failed')
        with pytest.raises(Exception):
            PineconeSovereignAgent(Path('/tmp'))

def test_embedding_dimension_validation(agent: Any) -> Any:
    """Brief description of functionality and purpose."""
    agent_instance, _ = agent
    long_emb: Any = [0.1] * 2000
    repaired: Any = agent_instance._validate_and_repair_embedding(long_emb, 'test')
    assert len(repaired) == 1536
    correct_emb: Any = [0.1] * 1536
    repaired: Any = agent_instance._validate_and_repair_embedding(correct_emb, 'test')
    assert len(repaired) == 1536
    assert repaired == correct_emb
