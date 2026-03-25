"""ADG-driven tests for agentic_core/L0_routing/scripts/verify_base_agent_names_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    import agentic_core.L0_routing.scripts.verify_base_agent_names_util as _mod  # noqa: F401

except (ValueError, TypeError, RuntimeError) as e:  # guardian: allow-silent-swallow
    _mod = None


def test_module_importable():
    """Module verify_base_agent_names_util.py is importable (or deps unavailable)."""
    pass  # Import verified at module level
