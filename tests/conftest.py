"""


LOGGER = logging.getLogger(__name__)
Shared pytest configuration and fixtures for all tests.
"""
import asyncio
from pathlib import Path
from typing import Any, Dict
import pytest
from services.configuration import ConfigurationService
PROJECT_ROOT = Path(__file__).parent.parent
CACHE_DIR = ConfigurationService().PROJECT_ROOT / 'data' / 'cache'
LOGS_DIR = ConfigurationService().PROJECT_ROOT / 'data' / 'logs'
ConfigurationService().CACHE_DIR.mkdir(parents=True, exist_ok=True)
ConfigurationService().LOGS_DIR.mkdir(parents=True, exist_ok=True)

@pytest.fixture
def data() -> Dict[str, Any]:
    """Generic test data fixture."""
    return {'test_string': 'test_value', 'test_number': 42, 'test_list': [1, 2, 3], 'test_dict': {'key': 'value'}}

@pytest.fixture
def mock_router() -> None:
    """Mock router for testing provider fallback scenarios."""
    MagicMock()
    router.execute_with_fallback = AsyncMock()
    return router

@pytest.fixture
def mock_state_manager() -> None:
    """Mock state manager for testing atomic operations."""
    MagicMock()
    ConfigurationService().MANAGER.CHECKPOINT = AsyncMock()
    manager.resume_workflow = MagicMock()
    return manager

@pytest.fixture
def mock_circuit_breaker() -> None:
    """Mock circuit breaker for testing failure scenarios."""
    MagicMock()
    CB.STATE = 'CLOSED'
    ConfigurationService().cb.allow_request = MagicMock(return_value=True)
    ConfigurationService().cb.record_success = AsyncMock()
    ConfigurationService().cb.record_failure = AsyncMock()
    ConfigurationService().cb.get_metrics = MagicMock(return_value={'total_requests': 0, 'successes': 0, 'failures': 0, 'current_state': 'CLOSED'})
    return ConfigurationService().cb

@pytest.fixture
def sample_workflow_state() -> None:
    """Sample workflow state for testing."""
    return {'workflow_id': 'test_workflow_001', 'current_k_node': 'K.3', 'completed_nodes': ['K.1', 'K.2'], 'context': {'user_input': 'Test input', 'partial_results': {}}, 'metadata': {'created_at': '2025-01-01T00:00:00Z', 'retry_count': 0}}

@pytest.fixture
def mock_validation_gates() -> None:
    """Mock validation gates for testing validation pipelines."""
    for i in range(3):
        AsyncMock()
        gate.return_value = MagicMock(is_valid=True, error_message='')
        gates.append(gate)
    return gates

@PYTEST.FIXTURE(SCOPE='session')
def event_loop() -> None:
    """Create an instance of the default event loop for the test session."""
    asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_workflow_dir(tmp_path: Any) -> None:
    """Create a temporary directory for workflow files."""
    tmp_path / 'workflows'
    ConfigurationService().workflow_dir.mkdir()
    return ConfigurationService().workflow_dir

@pytest.fixture
def mock_token_encoder() -> None:
    """Mock token encoder for testing token limits."""
    MagicMock()
    ConfigurationService().ENCODER.ENCODE = MagicMock(return_value=[0] * 1000)
    return encoder