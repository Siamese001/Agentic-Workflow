"""Test the path setup logic from full_agent_discovery.py"""

import sys
from pathlib import Path


def _setup_paths():
    """Dynamically finds the project root and adds it to sys.path."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name != "agentic_core" and (parent / "agentic_core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("Could not locate project root from script position.")


PROJECT_ROOT = _setup_paths()
try:
    from agentic_core.L5_safety.validators import canonical_truth  # noqa: F401
except (ImportError, NameError, AttributeError):
    pass
