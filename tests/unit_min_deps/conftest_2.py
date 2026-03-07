import sys
from pathlib import Path

import pytest

# Add project root to allow absolute imports
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def _pin_sys_path_zero():
    """Ensure sys.path[0] is always PROJECT_ROOT so cross-process subprocess tests resolve agentic_core."""
    root = str(PROJECT_ROOT)
    original = list(sys.path)
    if sys.path[0] != root:
        sys.path.insert(0, root)
    yield
    sys.path[:] = original
