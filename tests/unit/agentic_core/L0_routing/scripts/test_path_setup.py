import pytest

# Check if path_constants is available
try:
    from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
    from agentic_core.L5_safety.validators import canonical_truth
    PATH_SETUP_AVAILABLE = True
except ImportError:
    PATH_SETUP_AVAILABLE = False


"""Test the path setup logic from full_agent_discovery.py"""
import sys
from pathlib import Path


@pytest.mark.skipif(not PATH_SETUP_AVAILABLE, reason="path_constants not available")
def _setup_paths():
    """Dynamically finds the project root and adds it to sys.path."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name != AGENTIC_CORE_DIR and (parent / AGENTIC_CORE_DIR).exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError('Could not locate project root from script position.')
PROJECT_ROOT = _setup_paths()
