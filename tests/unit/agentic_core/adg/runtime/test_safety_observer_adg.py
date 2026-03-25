"""ADG importability contract for agentic_core/adg/runtime/safety_observer.py."""
from __future__ import annotations

import agentic_core.adg.runtime.safety_observer  # noqa: F401


def test_module_importable():
    """Module safety_observer must be importable."""
    assert agentic_core.adg.runtime.safety_observer is not None
