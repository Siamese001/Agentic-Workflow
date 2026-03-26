"""ADG contract tests for L4_state/types/validation_context_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L4_state.types.validation_context_types  # noqa: F401


def test_module_importable():
    import agentic_core.L4_state.types.validation_context_types  # noqa: F401
    """Module validation_context_types must be importable."""
    assert agentic_core.L4_state.types.validation_context_types is not None
