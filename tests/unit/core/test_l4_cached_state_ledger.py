import pytest
import json
from datetime import datetime
from unittest.mock import MagicMock, patch
from pathlib import Path
from agentic_core.L4_state.validation_context.cached_state_ledger import CachedStateLedger

@pytest.fixture
def state_ledger(tmp_path):
    """Mock setup for L4 state ledger testing."""
    with patch("agentic_core.L4_state.cache.redis_sovereign_agent.RedisSovereignAgent") as mock_agent:
        mock_client = MagicMock()
        mock_agent.return_value.get_client.return_value = mock_client
        ledger = CachedStateLedger(tmp_path, "test_session")
        return ledger, mock_client

def test_cache_validation_context(state_ledger):
    ledger, client = state_ledger
    test_key = "test_context"
    test_context = {
        "cycle_id": "123",
        "status": "active",
        "files_scanned": 50,
        "violations_found": 5
    }
    
    ledger.cache_validation_context(test_key, test_context)
    
    # Verify it was cached with correct prefix and TTL
    expected_key = "l4_context:test_session:test_context"
    client.set.assert_called_once_with(
        expected_key,
        json.dumps(test_context),
        ex=86400  # 24 hours
    )

def test_get_cached_validation_context_hit(state_ledger):
    ledger, client = state_ledger
    test_context = {"cycle_id": "123", "status": "active"}
    client.get.return_value = json.dumps(test_context)
    
    result = ledger.get_cached_validation_context("test_context")
    assert result == test_context

def test_get_cached_validation_context_miss(state_ledger):
    ledger, client = state_ledger
    client.get.return_value = None
    
    result = ledger.get_cached_validation_context("non_existent")
    assert result is None

def test_append_audit_trail(state_ledger):
    ledger, client = state_ledger
    test_event = {
        "timestamp": datetime.now().isoformat(),
        "action": "move",
        "file": "test.py",
        "agent": "TestAgent"
    }
    
    ledger.append_audit_trail(test_event)
    
    # Verify event was appended to correct list
    expected_key = "l4_audit:test_session"
    client.rpush.assert_called_once_with(
        expected_key,
        json.dumps(test_event)
    )
    # Verify TTL was set on the list
    client.expire.assert_called_once_with(expected_key, 31536000)  # 1 year

def test_get_audit_trail(state_ledger):
    ledger, client = state_ledger
    test_events = [
        {"action": "move", "file": "test1.py"},
        {"action": "archive", "file": "test2.py"}
    ]
    client.lrange.return_value = [json.dumps(e) for e in test_events]
    
    result = ledger.get_audit_trail()
    assert result == test_events
    client.lrange.assert_called_once_with("l4_audit:test_session", 0, -1)

def test_historian_cache_operations(state_ledger):
    ledger, client = state_ledger
    test_snapshot = {"state": "complete", "files": 100}
    
    # Test caching historian snapshot
    ledger.cache_historian_snapshot(test_snapshot)
    
    expected_key = "l4_historian:test_session"
    client.set.assert_called_once_with(
        expected_key,
        json.dumps(test_snapshot),
        ex=604800  # 7 days
    )

def test_invalidate_context_on_file_change(state_ledger):
    ledger, client = state_ledger
    file_path = Path("test/changed_file.py")
    
    # Mock scan to return context keys
    client.scan_iter.return_value = [
        "l4_context:test_session:changed_file_context",
        "l4_context:test_session:related_context"
    ]
    
    ledger.invalidate_context_by_file(file_path)
    
    # Verify matching context keys were deleted
    assert client.delete.call_count == 2

def test_error_handling_in_cache_operations(state_ledger):
    """Test that Redis errors don't crash the ledger."""
    ledger, client = state_ledger
    client.set.side_effect = Exception("Redis connection lost")
    
    # Should not raise exception
    ledger.cache_validation_context("test", {"data": "value"})
    
    # Should handle gracefully
    result = ledger.get_cached_validation_context("test")
    assert result is None
