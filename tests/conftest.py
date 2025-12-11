"""
Shared pytest configuration and fixtures for all tests.
"""

import os
import pytest
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
