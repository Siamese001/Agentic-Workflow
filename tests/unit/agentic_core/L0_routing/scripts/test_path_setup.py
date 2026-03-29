import pytest

# Lazy import fixtures - avoid collection-time errors

@pytest.fixture(scope="session")
def _lazy_agentic_core_L0_routing_config_path_constants_0():
    from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
    return type('_Import', (), {"AGENTIC_CORE_DIR": AGENTIC_CORE_DIR})

@pytest.fixture(scope="session")
def _lazy_agentic_core_L5_safety_validators_1():
    from agentic_core.L5_safety.validators import canonical_truth
    return type('_Import', (), {"canonical_truth": canonical_truth})

"""Test the path setup logic from full_agent_discovery.py"""
import sys
from pathlib import Path


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
