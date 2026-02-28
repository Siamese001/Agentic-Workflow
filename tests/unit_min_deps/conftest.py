import sys
from pathlib import Path

import pytest

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
