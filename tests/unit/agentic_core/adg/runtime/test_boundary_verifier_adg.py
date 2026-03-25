"""ADG importability contract for agentic_core/adg/runtime/boundary_verifier.py."""
from __future__ import annotations

import agentic_core.adg.runtime.boundary_verifier  # noqa: F401


def test_module_importable():
    """Module boundary_verifier must be importable."""
    assert agentic_core.adg.runtime.boundary_verifier is not None
