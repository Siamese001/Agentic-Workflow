import pytest
import json
from pathlib import Path
from agentic_core.L3_orchestration.workflow_engines.cached_orchestrator import CachedOrchestrator

@pytest.fixture
def orchestrator(tmp_path):
    # Mocking the Redis gateway inside the orchestrator
    with patch("agentic_core.L4_state.cache.redis_sovereign_agent.RedisSovereignAgent") as mock_agent:
        mock_client = MagicMock()
        mock_agent.return_value.get_client.return_value = mock_client
        engine = CachedOrchestrator(tmp_path, mission_id="test_hop")
        return engine, mock_client

def test_fission_decision_recall(orchestrator):
    engine, client = orchestrator
    file_path = Path("agentic_core/L1_cognition/brain.py")
    mock_decision = {"action": "fission", "lines": 500}
    
    # Setup the mock to 'remember'
    client.get.return_value = json.dumps(mock_decision)
    
    recall = engine.get_cached_fission(file_path)
    assert recall == mock_decision
    print("   [OK] L3 Recall verified.")

def test_fission_decision_cache(orchestrator):
    engine, client = orchestrator
    file_path = Path("agentic_core/L1_cognition/brain.py")
    decision = {"action": "fission", "lines": 500}
    
    engine.cache_fission_decision(file_path, decision)
    
    # Verify it was cached with correct key and TTL
    expected_key = f"l3_fission:test_hop:{file_path}"
    client.set.assert_called_once_with(
        expected_key,
        json.dumps(decision),
        ex=86400  # 24 hours
    )

def test_routing_cache_miss(orchestrator):
    engine, client = orchestrator
    client.get.return_value = None
    
    result = engine.get_cached_routing("test_task")
    assert result is None

def test_routing_cache_hit(orchestrator):
    engine, client = orchestrator
    mock_route = {"agent": "TestAgent", "confidence": 0.95}
    client.get.return_value = json.dumps(mock_route)
    
    result = engine.get_cached_routing("test_task")
    assert result == mock_route

def test_mission_checkpoint_persistence(orchestrator):
    engine, client = orchestrator
    
    engine.set_mission_checkpoint(5)
    
    # Verify checkpoint was saved
    client.set.assert_called_with(
        "l3_mission:test_hop:last_step",
        "5",
        ex=604800  # 7 days
    )

def test_mission_resume_from_checkpoint(orchestrator):
    engine, client = orchestrator
    client.get.return_value = "7"
    
    checkpoint = engine.get_last_checkpoint()
    assert checkpoint == 7

def test_invalidate_on_file_move(orchestrator):
    engine, client = orchestrator
    old_path = Path("old/location.py")
    new_path = Path("new/location.py")
    
    # Mock scan to return related keys
    client.scan_iter.return_value = [
        "l3_fission:test_hop:old/location.py",
        "l3_routing:test_hop:old_location_hash"
    ]
    
    engine.invalidate_on_file_move(old_path, new_path)
    
    # Verify old keys were deleted
    assert client.delete.call_count == 2
