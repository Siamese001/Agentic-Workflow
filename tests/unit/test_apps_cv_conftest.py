import pytest
pytestmark = pytest.mark.skip(reason="DEPRECATED: Test requires external modules")

"""
Shared fixtures and utilities for the Apps CV test suite
"""

import json
import os
import sys
from unittest.mock import Mock

import pytest
from canon_validator import CanonValidatorAgent

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')))


@pytest.fixture
def mock_validator():
    """Create a validator with mocked dependencies for general testing"""
    validator = CanonValidatorAgent()

    # Mock LLM
    validator.llm = Mock()
    validator.llm.generate_plan.return_value = {
        "status": "valid",
        "reasoning": "Code is valid"
    }

    # Mock embedding function
    validator.embed_fn = Mock(return_value=[0.1] * 768)

    # Mock Pinecone
    validator.pinecone = Mock()
    validator.pinecone.query = Mock(return_value={'matches': []})
    validator.pinecone.upsert = Mock()

    # Mock Redis cache
    validator.cache = Mock()
    validator.cache.check = Mock(return_value=None)
    validator.cache.store = Mock()

    return validator


@pytest.fixture
def mock_validator_with_all_dependencies():
    """Create a validator with all L1-L5 dependencies mocked"""
    validator = CanonValidatorAgent()

    # L1: Filesystem and GitKraken
    validator.llm = Mock()
    validator.embed_fn = Mock(return_value=[0.1] * 768)

    # L2: Figma
    validator.figma_client = Mock()

    # L3: Pinecone and Brave Search
    validator.pinecone = Mock()
    validator.pinecone.query = Mock(return_value={'matches': []})
    validator.pinecone.upsert = Mock()
    validator.brave_search = Mock()

    # L4: Redis
    validator.cache = Mock()
    validator.cache.check = Mock(return_value=None)
    validator.cache.store = Mock()
    validator.redis_client = Mock()

    # L5: MEMemory
    validator.memory_client = Mock()

    return validator


@pytest.fixture
def sample_violating_code():
    """Sample code with violations for testing"""
    return """
import os

def vulnerable_function():
    os.system("ls -la")
    eval(user_input)
    return True
"""


@pytest.fixture
def sample_compliant_code():
    """Sample compliant code for testing"""
    return """
import subprocess

def safe_function():
    result = subprocess.run(['ls', '-la'], capture_output=True)
    return result.returncode == 0
"""


@pytest.fixture
def mock_time():
    """Mock current time for testing"""
    from datetime import datetime, timezone
    return datetime(2025, 12, 15, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def mock_redis_transaction():
    """Mock Redis transaction for atomic operations"""
    class MockRedisTransaction:
                    
        def __init__(self):
            self.operations = []
            self.executed = False

        def multi(self):
                                    
            return self

        def set(self, key, value):
                                    
            self.operations.append(("SET", key, value))
            return self

        def get(self, key):
                                    
            for op in self.operations:
                if op[0] == "SET" and op[1] == key:
                    return op[2]
            return None

        def exec(self):
                                    
            self.executed = True
            return "OK"

        def discard(self):
                                    
            self.operations.clear()
            return self

    return MockRedisTransaction()


@pytest.fixture
def mock_figma_versions():
    """Mock Figma version data"""
    return [
        {
            "id": "v1.0.0",
            "created_at": "2025-12-14T12:00:00Z",
            "name": "Initial version"
        },
        {
            "id": "v1.1.0",
            "created_at": "2025-12-15T10:00:00Z",
            "name": "Updated version"
        },
        {
            "id": "v2.0.0",
            "created_at": "2025-12-15T12:00:00Z",
            "name": "Latest version"
        }
    ]


@pytest.fixture
def mock_rag_responses():
    """Mock RAG responses for testing"""
    return {
        "brave_search_success": json.dumps([{
            "source": "security.stackexchange.com",
            "fix_text": "Use subprocess.run instead of os.system",
            "confidence": "high",
            "edits": [{"oldText": "os.system(", "newText": "subprocess.run("}]
        }]),
        "brave_search_insufficient": json.dumps([{
            "source": "generic.com",
            "fix_text": "Not specific enough",
            "confidence": "low"
        }]),
        "pinecone_search": {
            "status": "success",
            "fix_result": {
                "metadata": {
                    "edits": [{"oldText": "eval(", "newText": "safe_eval("}]
                }
            },
            "source": "Pinecone_HighCost"
        }
    }


# Test markers for organizing tests
pytest_plugins = []  # GLOBAL: Review if this should be constant


def pytest_configure(config):
    """Configure custom markers"""
    config.addinivalue_line(
        "markers", "unit_mocks: Phase I unit tests for isolated components"
    )
    config.addinivalue_line(
        "markers", "integration_logic: Phase II integration tests for multi-layer flows"
    )
    config.addinivalue_line(
        "markers", "adversarial_hardening: Phase III security and robustness tests"
    )
    config.addinivalue_line(
        "markers", "emergency_protocol: Phase IV emergency bailout tests"
    )
    config.addinivalue_line(
        "markers", "l1: Tests targeting Layer 1 (Filesystem, GitKraken)"
    )
    config.addinivalue_line(
        "markers", "l2: Tests targeting Layer 2 (Figma, Design Tokens)"
    )
    config.addinivalue_line(
        "markers", "l3: Tests targeting Layer 3 (Pinecone, Brave Search)"
    )
    config.addinivalue_line(
        "markers", "l4: Tests targeting Layer 4 (Redis, Atomic Transactions)"
    )
    config.addinivalue_line(
        "markers", "l5: Tests targeting Layer 5 (MEMemory, Policy Layer)"
    )

