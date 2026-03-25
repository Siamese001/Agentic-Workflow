"""ADG importability contract for agentic_core/adg/runtime/config_governance.py."""
from __future__ import annotations

import agentic_core.adg.runtime.config_governance  # noqa: F401


def test_module_importable():
    """Module config_governance must be importable."""
    assert agentic_core.adg.runtime.config_governance is not None
