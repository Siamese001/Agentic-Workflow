"""ADG importability contract for agentic_core/adg/runtime/antipattern_registry.py."""
from __future__ import annotations

import agentic_core.adg.runtime.antipattern_registry  # noqa: F401


def test_module_importable():
    """Module antipattern_registry must be importable."""
    assert agentic_core.adg.runtime.antipattern_registry is not None
