import pytest
import json
from unittest.mock import MagicMock, patch
from pathlib import Path
from agentic_core.L4_state.cache.redis_sovereign_agent import RedisSovereignAgent

@pytest.fixture
def redis_agent(tmp_path):
    """Sovereign mock setup for Redis testing."""
    with patch("redis.Redis") as mock_redis:
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        # We assume success on init for the happy path
        mock_client.ping.return_value = True 
        agent = RedisSovereignAgent(tmp_path)
        return agent, mock_client

def test_cache_set_logic(redis_agent):
    agent, client = redis_agent
    test_key = "sovereign:test"
    test_val = {"status": "locked"}
    
    agent.cache_set(test_key, test_val)
    
    # Assert it was serialized and set with the correct TTL (7 days)
    client.set.assert_called_once_with(
        test_key, 
        json.dumps(test_val), 
        ex=604800
    )

def test_cache_miss_behavior(redis_agent):
    agent, client = redis_agent
    client.get.return_value = None
    
    result = agent.cache_get("non_existent_key")
    assert result is None # Sovereign acknowledgment of a cold cache

def test_cache_hit_behavior(redis_agent):
    agent, client = redis_agent
    test_data = {"action": "fission", "lines": 500}
    client.get.return_value = json.dumps(test_data)
    
    result = agent.cache_get("existing_key")
    assert result == test_data

def test_invalidate_by_path(redis_agent):
    agent, client = redis_agent
    # Mock scan to return keys
    client.scan_iter.return_value = [
        "l3_fission:abcdef123",
        "l4_context:abcdef123",
        "l5_gravity:abcdef123"
    ]
    
    agent.invalidate_by_path(Path("test/file.py"))
    
    # Verify all matching keys were deleted
    assert client.delete.call_count == 3

def test_connection_failure(redis_agent):
    """Test fail-fast behavior on Redis connection failure."""
    with patch("redis.Redis") as mock_redis:
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.side_effect = Exception("Connection refused")
        
        # Should raise exception on init
        with pytest.raises(Exception):
            RedisSovereignAgent(Path("/tmp"))
