"""ADG importability contract for agentic_core/L5_safety/utils/unified_cst_healer_util.py."""
from __future__ import annotations

import agentic_core.L5_safety.utils.unified_cst_healer_util  # noqa: F401


def test_module_importable():
    """Module unified_cst_healer_util must be importable."""
    assert agentic_core.L5_safety.utils.unified_cst_healer_util is not None
