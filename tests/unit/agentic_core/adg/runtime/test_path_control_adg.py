"""ADG importability contract for agentic_core/adg/runtime/path_control.py."""
from __future__ import annotations

import agentic_core.adg.runtime.path_control  # noqa: F401


def test_module_importable():
    """Module path_control must be importable."""
    assert agentic_core.adg.runtime.path_control is not None
