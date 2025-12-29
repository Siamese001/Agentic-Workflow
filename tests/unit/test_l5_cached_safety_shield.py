import pytest
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import json
from unittest.mock import MagicMock, patch
from pathlib import Path
from agentic_core.L5_safety.guardrails.cached_safety_shield import CachedSafetyShield

@pytest.fixture
def safety_shield(tmp_path: Any) -> Any:
    """Mock setup for L5 safety shield testing."""
    with patch('agentic_core.L4_state.cache.redis_sovereign_agent.RedisSovereignAgent') as mock_agent:
        mock_client: Any = MagicMock()
        mock_agent.return_value.get_client.return_value = mock_client
        shield: Any = CachedSafetyShield(tmp_path, 'test_session')
        return (shield, mock_client)

def test_cache_gravity_verdict(safety_shield: Any) -> Any:
    """Brief description of functionality and purpose."""
    shield, client = safety_shield
    test_file: Any = Path('agentic_core/test_file.py')
    test_verdict: Any = {'had_violations': True, 'healed': True}
    shield.cache_gravity_verdict(test_file, test_verdict)
    expected_key: Any = f'l5_gravity:test_session:{test_file.relative_to(Path.cwd())}'
    client.set.assert_called_once_with(expected_key, json.dumps(test_verdict), ex=604800)

def test_get_cached_gravity_hit(safety_shield: Any) -> Any:
    """Brief description of functionality and purpose."""
    shield, client = safety_shield
    test_file: Any = Path('test_file.py')
    test_verdict: Any = {'had_violations': True, 'healed': True}
    client.get.return_value = json.dumps(test_verdict)
    result: Any = shield.get_cached_gravity(test_file)
    assert result == test_verdict

def test_get_cached_gravity_miss(safety_shield: Any) -> Any:
    """Brief description of functionality and purpose."""
    shield, client = safety_shield
    test_file: Any = Path('non_existent.py')
    client.get.return_value = None
    result: Any = shield.get_cached_gravity(test_file)
    assert result is None

def test_cache_policy_verdict(safety_shield: Any) -> Any:
    """Brief description of functionality and purpose."""
    shield, client = safety_shield
    test_prompt: Any = 'Test prompt for policy check'
    test_verdict: Any = {'approved': False, 'reason': 'Violation detected'}
    shield.cache_policy_verdict(test_prompt, test_verdict)
    client.set.assert_called_once_with(f'l5_policy:test_session:{hash(test_prompt)}', json.dumps(test_verdict), ex=86400)

def test_get_cached_policy_hit(safety_shield: Any) -> Any:
    """Brief description of functionality and purpose."""
    shield, client = safety_shield
    test_prompt: Any = 'Test prompt'
    test_verdict: Any = {'approved': True}
    client.get.return_value = json.dumps(test_verdict)
    result: Any = shield.get_cached_policy(test_prompt)
    assert result == test_verdict

def test_get_cached_policy_miss(safety_shield: Any) -> Any:
    """Brief description of functionality and purpose."""
    shield, client = safety_shield
    client.get.return_value = None
    result: Any = shield.get_cached_policy('unknown_prompt')
    assert result is None

def test_guardrail_caching(safety_shield: Any) -> Any:
    """Brief description of functionality and purpose."""
    shield, client = safety_shield
    test_guard: Any = 'TestGuard'
    test_result: Any = {'passed': True, 'score': 0.95}
    shield.cache_guardrail_result(test_guard, test_result)
    expected_key: Any = f'l5_guardrail:test_session:{test_guard}'
    client.set.assert_called_once_with(expected_key, json.dumps(test_result), ex=86400)

def test_invalidate_on_policy_breach(safety_shield: Any) -> Any:
    """Brief description of functionality and purpose."""
    shield, client = safety_shield
    test_prompt: Any = 'breached_prompt'
    client.scan_iter.return_value = ['l5_policy:test_session:abc123', 'l5_policy:test_session:def456']
    shield.invalidate_policy_cache(test_prompt)
    assert client.delete.call_count == 2

def test_error_handling_in_safety_cache(safety_shield: Any) -> Any:
    """Test that Redis errors don't crash safety operations."""
    shield, client = safety_shield
    client.get.side_effect = Exception('Redis connection lost')
    result: Any = shield.get_cached_gravity(Path('test.py'))
    assert result is None
    client.get.side_effect = None
    client.set.side_effect = Exception('Redis write failed')
    shield.cache_gravity_verdict(Path('test.py'), {'test': 'data'})
