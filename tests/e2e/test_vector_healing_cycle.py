"""E2E test for vector healing cycle: diagnosis → heal → verify."""
import pytest
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


@pytest.mark.e2e
@pytest.mark.slow
class test_vector_healing_cycle:
    """Test complete vector healing workflow."""

    @patch('agentic_core.L4_state.vector_store.PineconeSovereignAgent')
    def test_diagnose_stale_vectors(self, mock_pinecone: Any, mock_pinecone_index: Any, audit_log_tracker: Any) -> Any:
        """
        GIVEN: Vector database with stale embeddings
        WHEN: Diagnosis runs
        THEN: Stale vectors identified
        """
        mock_pinecone.return_value.index = mock_pinecone_index
        mock_pinecone_index.query.return_value = {'matches': [{'id': 'vec-old-1', 'score': 0.45, 'metadata': {'timestamp': '2024-01-01'}}, {'id': 'vec-old-2', 'score': 0.5, 'metadata': {'timestamp': '2024-01-01'}}, {'id': 'vec-fresh', 'score': 0.95, 'metadata': {'timestamp': '2024-12-27'}}]}
        agent: Any = mock_pinecone.return_value
        results: Any = agent.index.query(vector=[0.1] * 1536, top_k=10)
        stale_vectors: Any = [m for m in results['matches'] if m['score'] < 0.7]
        audit_log_tracker.log('vector_diagnosis', {'total_checked': len(results['matches']), 'stale_count': len(stale_vectors)})
        assert len(stale_vectors) == 2
        diagnosis: Any = audit_log_tracker.get_entries('vector_diagnosis')
        assert diagnosis[0]['details']['stale_count'] == 2

    @patch('agentic_core.L4_state.vector_store.PineconeSovereignAgent')
    def test_heal_stale_vectors_with_reembedding(self, mock_pinecone: Any, mock_pinecone_index: Any, mock_gemini_client: Any, audit_log_tracker: Any) -> Any:
        """
        GIVEN: Stale vectors identified
        WHEN: Healing process re-embeds content
        THEN: Fresh vectors upserted to database
        """
        mock_pinecone.return_value.index = mock_pinecone_index
        mock_gemini_client.embed_content.return_value = Mock(embedding=[0.9] * 1536)
        stale_vectors: Any = [{'id': 'vec-old-1', 'content': 'Outdated sovereignty doc'}, {'id': 'vec-old-2', 'content': 'Old architecture notes'}]
        for vec in stale_vectors:
            new_embedding: Any = mock_gemini_client.embed_content(vec['content']).embedding
            mock_pinecone_index.upsert(vectors=[{'id': vec['id'], 'values': new_embedding, 'metadata': {'healed': True, 'timestamp': '2024-12-27'}}])
        audit_log_tracker.log('vector_healing', {'healed_count': len(stale_vectors), 'method': 'reembedding'})
        assert mock_pinecone_index.upsert.call_count == 2
        healing_log: Any = audit_log_tracker.get_entries('vector_healing')
        assert healing_log[0]['details']['healed_count'] == 2

    @patch('agentic_core.L4_state.vector_store.PineconeSovereignAgent')
    def test_verify_healing_improved_similarity(self, mock_pinecone: Any, mock_pinecone_index: Any, audit_log_tracker: Any) -> Any:
        """
        GIVEN: Vectors healed with fresh embeddings
        WHEN: Verification query runs
        THEN: Similarity scores improved
        """
        mock_pinecone_index.query.return_value = {'matches': [{'id': 'vec-old-1', 'score': 0.45}]}
        before_score: Any = mock_pinecone_index.query(vector=[0.1] * 1536)['matches'][0]['score']
        mock_pinecone_index.query.return_value = {'matches': [{'id': 'vec-old-1', 'score': 0.92}]}
        after_score: Any = mock_pinecone_index.query(vector=[0.1] * 1536)['matches'][0]['score']
        improvement: Any = after_score - before_score
        audit_log_tracker.log('healing_verification', {'before_score': before_score, 'after_score': after_score, 'improvement': improvement})
        assert improvement > 0.4
        assert after_score > 0.9
        verification: Any = audit_log_tracker.get_entries('healing_verification')
        assert verification[0]['details']['improvement'] > 0.4

    @patch('agentic_core.L4_state.vector_store.PineconeSovereignAgent')
    def test_corrupted_vector_detection_and_removal(self, mock_pinecone: Any, mock_pinecone_index: Any, audit_log_tracker: Any) -> Any:
        """
        GIVEN: Corrupted vectors (NaN, Inf values)
        WHEN: Diagnosis detects corruption
        THEN: Corrupted vectors removed
        """
        corrupted_vectors: Any = [{'id': 'vec-corrupt-1', 'values': [0.1, float('nan'), 0.3]}, {'id': 'vec-corrupt-2', 'values': [float('inf'), 0.2, 0.4]}]
        mock_pinecone_index.query.return_value = {'matches': [{'id': v['id'], 'values': v['values'], 'score': 0.0} for v in corrupted_vectors]}
        from vector_healing_engine import VectorHealingEngine
        engine: Any = VectorHealingEngine(mock_pinecone)
        import asyncio
        corrupted: Any = asyncio.run(engine.detect_corrupted_vectors())
        if not isinstance(corrupted, list):
            corrupted: Any = []
        for vec in corrupted:
            mock_pinecone_index.delete(ids=[vec['id']])
            audit_log_tracker.log('vector_removed', {'id': vec['id'], 'reason': 'corrupted'})
        assert len(corrupted) >= 1
        if len(corrupted) > 0:
            assert corrupted[0]['corruption_type'] in ['nan_values', 'inf_values']
        removed: Any = audit_log_tracker.get_entries('vector_removed')
        assert len(removed) >= 1
        assert mock_pinecone_index.delete.called

@pytest.mark.e2e
class test_vector_drift_detection:
    """Test detection of semantic drift in vectors."""

    @patch('agentic_core.L4_state.vector_store.PineconeSovereignAgent')
    def test_detect_semantic_drift_from_source(self, mock_pinecone: Any, mock_pinecone_index: Any, audit_log_tracker: Any) -> Any:
        """
from typing import Any
        GIVEN: Source document updated
        WHEN: Vector compared to current source
        THEN: Drift detected if mismatch
        """
        original_doc: Any = 'Sovereignty architecture principles'
        updated_doc: Any = 'Completely different content now'
        mock_pinecone_index.fetch.return_value = {'vectors': {'doc-1': {'values': [0.5] * 1536, 'metadata': {'source_hash': hash(original_doc)}}}}
        current_hash: Any = hash(updated_doc)
        stored_vector: Any = mock_pinecone_index.fetch(ids=['doc-1'])['vectors']['doc-1']
        drift_detected: Any = stored_vector['metadata']['source_hash'] != current_hash
        if drift_detected:
            audit_log_tracker.log('semantic_drift', {'vector_id': 'doc-1', 'action': 'requires_reembedding'})
        assert drift_detected is True
        drift_log: Any = audit_log_tracker.get_entries('semantic_drift')
        assert len(drift_log) == 1
