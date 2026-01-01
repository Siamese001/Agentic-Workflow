import pytest
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from agentic_core.L3_orchestration.workflow_engines.cached_orchestrator import CachedOrchestrator

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
from typing import Any
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


@pytest.fixture
def orchestrator(tmp_path: Any) -> Any:
    """Brief description of functionality and purpose."""
    with patch('agentic_core.L4_state.cache.redis_sovereign_agent.RedisSovereignAgent') as mock_agent:
        mock_client: Any = MagicMock()
        mock_agent.return_value.get_client.return_value = mock_client
        engine: Any = CachedOrchestrator(tmp_path, mission_id='test_hop')
        return (engine, mock_client)

def test_fission_decision_recall(orchestrator: Any) -> Any:
    """Brief description of functionality and purpose."""
    engine, client = orchestrator
    file_path: Any = Path('agentic_core/L1_cognition/brain.py')
    mock_decision: Any = {'action': 'fission', 'lines': 500}
    client.get.return_value = json.dumps(mock_decision)
    recall: Any = engine.get_cached_fission(file_path)
    assert recall == mock_decision
    print('   [OK] L3 Recall verified.')

def test_fission_decision_cache(orchestrator: Any) -> Any:
    """Brief description of functionality and purpose."""
    engine, client = orchestrator
    file_path: Any = Path('agentic_core/L1_cognition/brain.py')
    decision: Any = {'action': 'fission', 'lines': 500}
    engine.cache_fission_decision(file_path, decision)
    expected_key: Any = f'l3_fission:test_hop:{file_path}'
    client.set.assert_called_once_with(expected_key, json.dumps(decision), ex=86400)

def test_routing_cache_miss(orchestrator: Any) -> Any:
    """Brief description of functionality and purpose."""
    engine, client = orchestrator
    client.get.return_value = None
    result: Any = engine.get_cached_routing('test_task')
    assert result is None

def test_routing_cache_hit(orchestrator: Any) -> Any:
    """Brief description of functionality and purpose."""
    engine, client = orchestrator
    mock_route: Any = {'agent': 'TestAgent', 'confidence': 0.95}
    client.get.return_value = json.dumps(mock_route)
    result: Any = engine.get_cached_routing('test_task')
    assert result == mock_route

def test_mission_checkpoint_persistence(orchestrator: Any) -> Any:
    """Brief description of functionality and purpose."""
    engine, client = orchestrator
    engine.set_mission_checkpoint(5)
    client.set.assert_called_with('l3_mission:test_hop:last_step', '5', ex=604800)

def test_mission_resume_from_checkpoint(orchestrator: Any) -> Any:
    """Brief description of functionality and purpose."""
    engine, client = orchestrator
    client.get.return_value = '7'
    checkpoint: Any = engine.get_last_checkpoint()
    assert checkpoint == 7

def test_invalidate_on_file_move(orchestrator: Any) -> Any:
    """Brief description of functionality and purpose."""
    engine, client = orchestrator
    old_path: Any = Path('old/location.py')
    new_path: Any = Path('new/location.py')
    client.scan_iter.return_value = ['l3_fission:test_hop:old/location.py', 'l3_routing:test_hop:old_location_hash']
    engine.invalidate_on_file_move(old_path, new_path)
    assert client.delete.call_count == 2
