"""ADG importability contract for agentic_core/runtime/utils/trait_system_util.py."""
from __future__ import annotations

import agentic_core.runtime.utils.trait_system_util  # noqa: F401


def test_module_importable():
    """Module trait_system_util must be importable."""
    assert agentic_core.runtime.utils.trait_system_util is not None
