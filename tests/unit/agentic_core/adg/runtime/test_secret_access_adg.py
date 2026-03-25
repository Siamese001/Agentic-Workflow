"""ADG importability contract for agentic_core/adg/runtime/secret_access.py."""
from __future__ import annotations

import agentic_core.adg.runtime.secret_access  # noqa: F401


def test_module_importable():
    """Module secret_access must be importable."""
    assert agentic_core.adg.runtime.secret_access is not None
