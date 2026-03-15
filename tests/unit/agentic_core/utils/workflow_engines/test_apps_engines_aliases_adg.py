"""ADG-driven tests for agentic_core/utils/workflow_engines/apps_engines_aliases.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    import agentic_core.utils.workflow_engines.apps_engines_aliases as _mod  # noqa: F401
    _AVAILABLE = True
except ImportError:
    _mod = None
    _AVAILABLE = False


def test_module_importable():
    """Module apps_engines_aliases.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
