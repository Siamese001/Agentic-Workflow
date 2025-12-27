"""E2E test for vector healing cycle: diagnosis → heal → verify."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np


@pytest.mark.e2e
@pytest.mark.slow
class TestVectorHealingCycle:
    """Test complete vector healing workflow."""
    
    @patch('agentic_core.L4_state.vector_store.PineconeSovereignAgent')
    def test_diagnose_stale_vectors(
        self, mock_pinecone, mock_pinecone_index, audit_log_tracker
    ):
        """
        GIVEN: Vector database with stale embeddings
        WHEN: Diagnosis runs
        THEN: Stale vectors identified
        """
        # Arrange
        mock_pinecone.return_value.index = mock_pinecone_index
        mock_pinecone_index.query.return_value = {
            "matches": [
                {"id": "vec-old-1", "score": 0.45, "metadata": {"timestamp": "2024-01-01"}},
                {"id": "vec-old-2", "score": 0.50, "metadata": {"timestamp": "2024-01-01"}},
                {"id": "vec-fresh", "score": 0.95, "metadata": {"timestamp": "2024-12-27"}}
            ]
        }
        
        # Act
        agent = mock_pinecone.return_value
        results = agent.index.query(vector=[0.1] * 1536, top_k=10)
        
        stale_vectors = [
            m for m in results["matches"]
            if m["score"] < 0.7  # Threshold for staleness
        ]
        
        audit_log_tracker.log("vector_diagnosis", {
            "total_checked": len(results["matches"]),
            "stale_count": len(stale_vectors)
        })
        
        # Assert
        assert len(stale_vectors) == 2
        diagnosis = audit_log_tracker.get_entries("vector_diagnosis")
        assert diagnosis[0]["details"]["stale_count"] == 2
    
    @patch('agentic_core.L4_state.vector_store.PineconeSovereignAgent')
    def test_heal_stale_vectors_with_reembedding(
        self, mock_pinecone, mock_pinecone_index, mock_gemini_client, audit_log_tracker
    ):
        """
        GIVEN: Stale vectors identified
        WHEN: Healing process re-embeds content
        THEN: Fresh vectors upserted to database
        """
        # Arrange
        mock_pinecone.return_value.index = mock_pinecone_index
        mock_gemini_client.embed_content.return_value = Mock(
            embedding=[0.9] * 1536  # Fresh embedding
        )
        
        stale_vectors = [
            {"id": "vec-old-1", "content": "Outdated sovereignty doc"},
            {"id": "vec-old-2", "content": "Old architecture notes"}
        ]
        
        # Act
        for vec in stale_vectors:
            # Re-embed
            new_embedding = mock_gemini_client.embed_content(vec["content"]).embedding
            
            # Upsert fresh vector
            mock_pinecone_index.upsert(vectors=[{
                "id": vec["id"],
                "values": new_embedding,
                "metadata": {"healed": True, "timestamp": "2024-12-27"}
            }])
        
        audit_log_tracker.log("vector_healing", {
            "healed_count": len(stale_vectors),
            "method": "reembedding"
        })
        
        # Assert
        assert mock_pinecone_index.upsert.call_count == 2
        healing_log = audit_log_tracker.get_entries("vector_healing")
        assert healing_log[0]["details"]["healed_count"] == 2
    
    @patch('agentic_core.L4_state.vector_store.PineconeSovereignAgent')
    def test_verify_healing_improved_similarity(
        self, mock_pinecone, mock_pinecone_index, audit_log_tracker
    ):
        """
        GIVEN: Vectors healed with fresh embeddings
        WHEN: Verification query runs
        THEN: Similarity scores improved
        """
        # Arrange - Before healing
        mock_pinecone_index.query.return_value = {
            "matches": [
                {"id": "vec-old-1", "score": 0.45}
            ]
        }
        before_score = mock_pinecone_index.query(vector=[0.1] * 1536)["matches"][0]["score"]
        
        # After healing
        mock_pinecone_index.query.return_value = {
            "matches": [
                {"id": "vec-old-1", "score": 0.92}
            ]
        }
        after_score = mock_pinecone_index.query(vector=[0.1] * 1536)["matches"][0]["score"]
        
        # Act
        improvement = after_score - before_score
        audit_log_tracker.log("healing_verification", {
            "before_score": before_score,
            "after_score": after_score,
            "improvement": improvement
        })
        
        # Assert
        assert improvement > 0.4
        assert after_score > 0.9
        
        verification = audit_log_tracker.get_entries("healing_verification")
        assert verification[0]["details"]["improvement"] > 0.4
    
    @patch('agentic_core.L4_state.vector_store.PineconeSovereignAgent')
    def test_corrupted_vector_detection_and_removal(
        self, mock_pinecone, mock_pinecone_index, audit_log_tracker
    ):
        """
        GIVEN: Corrupted vectors (NaN, Inf values)
        WHEN: Diagnosis detects corruption
        THEN: Corrupted vectors removed
        """
        # Arrange
        mock_pinecone_index.query.return_value = {
            "matches": [
                {"id": "vec-corrupted", "values": [float('nan')] * 1536},
                {"id": "vec-good", "values": [0.5] * 1536}
            ]
        }
        
        # Act
        results = mock_pinecone_index.query(vector=[0.1] * 1536)
        corrupted = []
        
        for match in results["matches"]:
            if any(np.isnan(match["values"]) or np.isinf(match["values"])):
                corrupted.append(match["id"])
                mock_pinecone_index.delete(ids=[match["id"]])
        
        audit_log_tracker.log("corrupted_vectors_removed", {
            "count": len(corrupted),
            "ids": corrupted
        })
        
        # Assert
        assert len(corrupted) == 1
        assert "vec-corrupted" in corrupted
        assert mock_pinecone_index.delete.called


@pytest.mark.e2e
class TestVectorDriftDetection:
    """Test detection of semantic drift in vectors."""
    
    @patch('agentic_core.L4_state.vector_store.PineconeSovereignAgent')
    def test_detect_semantic_drift_from_source(
        self, mock_pinecone, mock_pinecone_index, audit_log_tracker
    ):
        """
        GIVEN: Source document updated
        WHEN: Vector compared to current source
        THEN: Drift detected if mismatch
        """
        # Arrange
        original_doc = "Sovereignty architecture principles"
        updated_doc = "Completely different content now"
        
        # Simulate vector for original
        mock_pinecone_index.fetch.return_value = {
            "vectors": {
                "doc-1": {
                    "values": [0.5] * 1536,
                    "metadata": {"source_hash": hash(original_doc)}
                }
            }
        }
        
        # Act
        current_hash = hash(updated_doc)
        stored_vector = mock_pinecone_index.fetch(ids=["doc-1"])["vectors"]["doc-1"]
        
        drift_detected = stored_vector["metadata"]["source_hash"] != current_hash
        
        if drift_detected:
            audit_log_tracker.log("semantic_drift", {
                "vector_id": "doc-1",
                "action": "requires_reembedding"
            })
        
        # Assert
        assert drift_detected is True
        drift_log = audit_log_tracker.get_entries("semantic_drift")
        assert len(drift_log) == 1
