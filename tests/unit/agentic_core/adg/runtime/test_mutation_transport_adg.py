"""ADG importability contract for agentic_core/adg/runtime/mutation_transport.py."""
from __future__ import annotations

import agentic_core.adg.runtime.mutation_transport  # noqa: F401


def test_module_importable():
    """Module mutation_transport must be importable."""
    assert agentic_core.adg.runtime.mutation_transport is not None
