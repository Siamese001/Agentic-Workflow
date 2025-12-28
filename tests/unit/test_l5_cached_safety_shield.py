import pytest
import json
from unittest.mock import MagicMock, patch
from pathlib import Path
from agentic_core.L5_safety.guardrails.cached_safety_shield import CachedSafetyShield

@pytest.fixture
def safety_shield(tmp_path):
    """Mock setup for L5 safety shield testing."""
    with patch("agentic_core.L4_state.cache.redis_sovereign_agent.RedisSovereignAgent") as mock_agent:
        mock_client = MagicMock()
        mock_agent.return_value.get_client.return_value = mock_client
        shield = CachedSafetyShield(tmp_path, "test_session")
        return shield, mock_client

def test_cache_gravity_verdict(safety_shield):
    shield, client = safety_shield
    test_file = Path("agentic_core/test_file.py")
    test_verdict = {"had_violations": True, "healed": True}
    
    shield.cache_gravity_verdict(test_file, test_verdict)
    
    # Verify it was cached with correct key and TTL
    expected_key = f"l5_gravity:test_session:{test_file.relative_to(Path.cwd())}"
    client.set.assert_called_once_with(
        expected_key,
        json.dumps(test_verdict),
        ex=604800  # 7 days
    )

def test_get_cached_gravity_hit(safety_shield):
    shield, client = safety_shield
    test_file = Path("test_file.py")
    test_verdict = {"had_violations": True, "healed": True}
    client.get.return_value = json.dumps(test_verdict)
    
    result = shield.get_cached_gravity(test_file)
    assert result == test_verdict

def test_get_cached_gravity_miss(safety_shield):
    shield, client = safety_shield
    test_file = Path("non_existent.py")
    client.get.return_value = None
    
    result = shield.get_cached_gravity(test_file)
    assert result is None

def test_cache_policy_verdict(safety_shield):
    shield, client = safety_shield
    test_prompt = "Test prompt for policy check"
    test_verdict = {"approved": False, "reason": "Violation detected"}
    
    shield.cache_policy_verdict(test_prompt, test_verdict)
    
    # Verify it was cached with correct key and TTL
    client.set.assert_called_once_with(
        f"l5_policy:test_session:{hash(test_prompt)}",
        json.dumps(test_verdict),
        ex=86400  # 24 hours
    )

def test_get_cached_policy_hit(safety_shield):
    shield, client = safety_shield
    test_prompt = "Test prompt"
    test_verdict = {"approved": True}
    client.get.return_value = json.dumps(test_verdict)
    
    result = shield.get_cached_policy(test_prompt)
    assert result == test_verdict

def test_get_cached_policy_miss(safety_shield):
    shield, client = safety_shield
    client.get.return_value = None
    
    result = shield.get_cached_policy("unknown_prompt")
    assert result is None

def test_guardrail_caching(safety_shield):
    shield, client = safety_shield
    test_guard = "TestGuard"
    test_result = {"passed": True, "score": 0.95}
    
    # Test caching guardrail result
    shield.cache_guardrail_result(test_guard, test_result)
    
    expected_key = f"l5_guardrail:test_session:{test_guard}"
    client.set.assert_called_once_with(
        expected_key,
        json.dumps(test_result),
        ex=86400  # 24 hours
    )

def test_invalidate_on_policy_breach(safety_shield):
    shield, client = safety_shield
    test_prompt = "breached_prompt"
    
    # Mock scan to return related policy keys
    client.scan_iter.return_value = [
        "l5_policy:test_session:abc123",
        "l5_policy:test_session:def456"
    ]
    
    shield.invalidate_policy_cache(test_prompt)
    
    # Verify policy keys were deleted
    assert client.delete.call_count == 2

def test_error_handling_in_safety_cache(safety_shield):
    """Test that Redis errors don't crash safety operations."""
    shield, client = safety_shield
    client.get.side_effect = Exception("Redis connection lost")
    
    # Should not raise exception
    result = shield.get_cached_gravity(Path("test.py"))
    assert result is None
    
    # Should handle gracefully on cache operations
    client.get.side_effect = None
    client.set.side_effect = Exception("Redis write failed")
    shield.cache_gravity_verdict(Path("test.py"), {"test": "data"})
