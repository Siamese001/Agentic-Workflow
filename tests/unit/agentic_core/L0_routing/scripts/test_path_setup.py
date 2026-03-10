"""Test the path setup logic from full_agent_discovery.py"""

import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
)


def _setup_paths():
    """Dynamically finds the project root and adds it to sys.path."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name != AGENTIC_CORE_DIR and (parent / AGENTIC_CORE_DIR).exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("Could not locate project root from script position.")


PROJECT_ROOT = _setup_paths()
try:
    from agentic_core.L5_safety.validators import canonical_truth  # noqa: F401
except (ImportError, NameError, AttributeError):
    pass
