"""ADG-driven tests for agentic_core/L4_state/engines/error_context_preserver.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L4_state.engines.error_context_preserver  # noqa: F401


def test_module_importable():
        import agentic_core.L4_state.engines.error_context_preserver  # noqa: F401
        """Module error_context_preserver must be importable."""
        assert agentic_core.L4_state.engines.error_context_preserver is not None

    assert agentic_core.L4_state.engines.error_context_preserver is not None
