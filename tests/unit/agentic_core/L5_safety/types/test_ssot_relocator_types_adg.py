"""ADG contract tests for L5_safety/types/ssot_relocator_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.types.ssot_relocator_types  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.types.ssot_relocator_types  # noqa: F401
    """Module ssot_relocator_types must be importable."""
    assert agentic_core.L5_safety.types.ssot_relocator_types is not None
