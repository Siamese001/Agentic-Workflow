"""ADG contract tests for L5_safety/types/sovereign_base_model_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.types.sovereign_base_model_types  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.types.sovereign_base_model_types  # noqa: F401
    """Module sovereign_base_model_types must be importable."""
    assert agentic_core.L5_safety.types.sovereign_base_model_types is not None
