"""ADG importability contract for agentic_core/L0_routing/utils/core_integrity_util.py."""
from __future__ import annotations

import agentic_core.L0_routing.utils.core_integrity_util  # noqa: F401


def test_module_importable():
    """Module core_integrity_util must be importable."""
    assert agentic_core.L0_routing.utils.core_integrity_util is not None
