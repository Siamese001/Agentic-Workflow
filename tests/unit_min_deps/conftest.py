import sys
from pathlib import Path

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Add project root to allow absolute imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def _inject_test_key_source():
    """Inject a deterministic TestKeySource for all unit_min_deps tests."""
    from agentic_core.L2_execution.enforcement.key_source import (
        TestKeySource,
        inject_key_source,
    )

    inject_key_source(TestKeySource())
