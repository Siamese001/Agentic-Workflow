"""Foundational behavioral tests for agentic_core/L5_safety/core_kernel/classification_kernel.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.core_kernel.classification_kernel  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.core_kernel.classification_kernel  # noqa: F401
    """Module classification_kernel must be importable."""
    assert agentic_core.L5_safety.core_kernel.classification_kernel is not None
