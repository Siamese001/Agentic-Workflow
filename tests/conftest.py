"""

logger = logging.getLogger(__name__)
Shared pytest configuration and fixtures for all tests.
"""

import pytest
import asyncio
from pathlib import Path
from typing import Dict, Any

# Test infrastructure constants
PROJECT_ROOT = Path(__file__).parent.parent
CACHE_DIR = PROJECT_ROOT / "data" / "cache"
LOGS_DIR = PROJECT_ROOT / "data" / "logs"
DEFAULT_MAX_RETRIES = 3

# Ensure directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

@pytest.fixture
def data() -> Dict[str, Any]:
    """Generic test data fixture."""
    return {
        "test_string": "test_value",
        "test_number": 42,
        "test_list": [1, 2, 3],
        "test_dict": {"key": "value"},
    }

@pytest.fixture
def mock_router():
    """Mock router for testing provider fallback scenarios."""
    router = MagicMock()
    router.execute_with_fallback = AsyncMock()
    return router

@pytest.fixture
def mock_state_manager():
    """Mock state manager for testing atomic operations."""
    manager = MagicMock()
    manager.checkpoint = AsyncMock()
    manager.resume_workflow = MagicMock()
    return manager

@pytest.fixture
def mock_circuit_breaker():
    """Mock circuit breaker for testing failure scenarios."""
    cb = MagicMock()
    cb.state = "CLOSED"
    cb.allow_request = MagicMock(return_value=True)
    cb.record_success = AsyncMock()
    cb.record_failure = AsyncMock()
    cb.get_metrics = MagicMock(return_value={
        'total_requests': 0,
        'successes': 0,
        'failures': 0,
        'current_state': 'CLOSED'
    })
    return cb

@pytest.fixture
def sample_workflow_state():
    """Sample workflow state for testing."""
    return {
        "workflow_id": "test_workflow_001",
        "current_k_node": "K.3",
        "completed_nodes": ["K.1", "K.2"],
        "context": {
            "user_input": "Test input",
            "partial_results": {}
        },
        "metadata": {
            "created_at": "2025-01-01T00:00:00Z",
            "retry_count": 0
        }
    }

@pytest.fixture
def mock_validation_gates():
    """Mock validation gates for testing validation pipelines."""
    gates = []
    for i in range(3):
        gate = AsyncMock()
        gate.return_value = MagicMock(is_valid=True, error_message="")
        gates.append(gate)
    return gates

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_workflow_dir(tmp_path):
    """Create a temporary directory for workflow files."""
    workflow_dir = tmp_path / "workflows"
    workflow_dir.mkdir()
    return workflow_dir

@pytest.fixture
def mock_token_encoder():
    """Mock token encoder for testing token limits."""
    encoder = MagicMock()
    encoder.encode = MagicMock(return_value=[0] * 1000)  # Default to 1000 tokens
    return encoder
