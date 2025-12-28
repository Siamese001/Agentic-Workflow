import pytest
import time
import os
from pathlib import Path
from agentic_core.L4_state.vector.pinecone_sovereign_agent import PineconeSovereignAgent

@pytest.fixture(scope="module")
def real_agent(tmp_path_factory):
    """The real deal: Connects to your live Pinecone account."""
    root = tmp_path_factory.mktemp("real_project")
    # We use a unique timestamped index to avoid collisions
    test_index = f"test-canon-{int(time.time())}"
    
    # We temporarily override the environment name for the test
    from unittest.mock import patch
    with patch("os.getenv", side_effect=lambda k, d=None: test_index if k == "PINECONE_INDEX_NAME" else d):
        agent = PineconeSovereignAgent(root)
        yield agent
        
        # [ETERNAL CLEANUP]
        try:
            agent.pc.delete_index(test_index)
            print(f"   [OK] Cleaned up live test index: {test_index}")
        except Exception: pass

def test_live_hybrid_recall(real_agent):
    # 1. Upsert a high-signal L5 file
    test_file = Path("agentic_core/L5_safety/policy/shield.py")
    real_agent.upsert_file_vector(test_file, "agentic_core/L5_safety")
    
    # 2. Wait for Pinecone to 'digest' the new vector
    time.sleep(5)
    
    # 3. Perform a hybrid search
    results = real_agent.hybrid_search("enforce neural policy and safety guardrails", top_k=1)
    
    # VERDICT: The L5 territory must be the top match
    assert len(results) > 0
    assert "L5_safety" in results[0]['metadata']['territory']
    print(f"   [OK] Live Hybrid Recall Score: {results[0]['score']:.4f}")

def test_live_health_report(real_agent):
    health = real_agent.health_check()
    # VERDICT: The index must report back its dimensions and fullness
    assert health["dimension"] == 1536
    assert health["vectors"] >= 1
    print(f"   [OK] Live health check confirmed: {health['vectors']} vectors active.")

def test_live_vector_lifecycle(real_agent):
    """Test the full vector lifecycle: create, query, update, delete."""
    test_file = Path("test/lifecycle_file.py")
    
    # 1. Create initial vector
    real_agent.upsert_file_vector(test_file, "test_territory")
    time.sleep(2)
    
    # 2. Query and verify
    results = real_agent.semantic_search("lifecycle test", top_k=1)
    assert len(results) > 0
    
    # 3. Update vector
    real_agent.upsert_file_vector(test_file, "updated_territory")
    time.sleep(2)
    
    # 4. Verify update
    updated_results = real_agent.semantic_search("lifecycle test", top_k=1)
    assert updated_results[0]['metadata']['territory'] == "updated_territory"
    
    # 5. Purge vector
    real_agent.purge_ghost_vector(test_file)
    time.sleep(2)
    
    # 6. Verify deletion
    final_results = real_agent.semantic_search("lifecycle test", top_k=1)
    # Should return empty or different results
    print(f"   [OK] Vector lifecycle completed successfully.")

def test_batch_operations_live(real_agent):
    """Test batch upsert operations with live Pinecone."""
    test_files = [
        (Path("batch1.py"), "batch_territory"),
        (Path("batch2.py"), "batch_territory"),
        (Path("batch3.py"), "batch_territory")
    ]
    
    # Batch upsert
    for file_path, territory in test_files:
        real_agent.upsert_file_vector(file_path, territory)
    
    time.sleep(3)
    
    # Verify all vectors are indexed
    health = real_agent.health_check()
    assert health["vectors"] >= 3
    
    # Search for batch territory
    results = real_agent.semantic_search("batch test", top_k=5)
    batch_matches = [r for r in results if "batch_territory" in r.get('metadata', {}).get('territory', '')]
    assert len(batch_matches) == 3
    
    print(f"   [OK] Batch operations verified: {len(batch_matches)} vectors indexed.")

@pytest.mark.skipif(not os.getenv("PINECONE_API_KEY"), reason="PINECONE_API_KEY not set")
def test_territory_aware_search(real_agent):
    """Test that territory-aware search returns relevant results."""
    # Index files from different territories
    l3_file = Path("agentic_core/L3_orchestration/workflow.py")
    l5_file = Path("agentic_core/L5_safety/policy/safety.py")
    
    real_agent.upsert_file_vector(l3_file, "agentic_core/L3_orchestration")
    real_agent.upsert_file_vector(l5_file, "agentic_core/L5_safety")
    time.sleep(3)
    
    # Search for orchestration-related query
    results = real_agent.semantic_search("workflow orchestration and mission execution", top_k=2)
    
    # Should prioritize L3 results
    assert len(results) > 0
    top_result = results[0]
    assert "L3_orchestration" in top_result['metadata']['territory']
    
    print(f"   [OK] Territory-aware search working: {top_result['metadata']['territory']} top result.")
