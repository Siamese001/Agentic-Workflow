"""ADG contract tests for L4_state/types/cycle_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L4_state.types.cycle_types  # noqa: F401


def test_module_importable():
    import agentic_core.L4_state.types.cycle_types  # noqa: F401
    """Module cycle_types must be importable."""
    assert agentic_core.L4_state.types.cycle_types is not None
