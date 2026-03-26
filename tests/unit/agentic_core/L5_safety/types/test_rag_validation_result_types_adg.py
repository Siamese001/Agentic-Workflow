"""ADG contract tests for L5_safety/types/rag_validation_result_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.types.rag_validation_result_types  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.types.rag_validation_result_types  # noqa: F401
    """Module rag_validation_result_types must be importable."""
    assert agentic_core.L5_safety.types.rag_validation_result_types is not None
