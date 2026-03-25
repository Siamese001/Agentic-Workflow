"""ADG importability contract for agentic_core/L5_safety/types/cst_transformers_types.py."""
from __future__ import annotations

import agentic_core.L5_safety.types.cst_transformers_types  # noqa: F401


def test_module_importable():
    """Module cst_transformers_types must be importable."""
    assert agentic_core.L5_safety.types.cst_transformers_types is not None
