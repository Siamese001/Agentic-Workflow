"""ADG contract tests for agentic_core/L5_safety/types/meta_learning_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.types.meta_learning_types  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.types.meta_learning_types  # noqa: F401
        """Module meta_learning_types must be importable."""
        assert agentic_core.L5_safety.types.meta_learning_types is not None

    assert agentic_core.L5_safety.types.meta_learning_types is not None
