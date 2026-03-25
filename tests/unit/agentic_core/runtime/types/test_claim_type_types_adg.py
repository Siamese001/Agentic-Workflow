"""ADG importability contract for agentic_core/runtime/types/claim_type_types.py."""
from __future__ import annotations

import agentic_core.runtime.types.claim_type_types  # noqa: F401


def test_module_importable():
    """Module claim_type_types must be importable."""
    assert agentic_core.runtime.types.claim_type_types is not None
