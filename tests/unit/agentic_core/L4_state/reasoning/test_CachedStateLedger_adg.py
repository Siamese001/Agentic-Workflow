"""ADG-driven tests for agentic_core/L4_state/reasoning/CachedStateLedger.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L4_state.reasoning.CachedStateLedger  # noqa: F401


def test_module_importable():
        import agentic_core.L4_state.reasoning.CachedStateLedger  # noqa: F401
        """Module CachedStateLedger must be importable."""
        assert agentic_core.L4_state.reasoning.CachedStateLedger is not None

    assert agentic_core.L4_state.reasoning.CachedStateLedger is not None
