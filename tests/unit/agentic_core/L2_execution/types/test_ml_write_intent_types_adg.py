"""ADG importability contract for agentic_core/L2_execution/types/ml_write_intent_types.py."""
from __future__ import annotations

import agentic_core.L2_execution.types.ml_write_intent_types  # noqa: F401


def test_module_importable():
    """Module ml_write_intent_types must be importable."""
    assert agentic_core.L2_execution.types.ml_write_intent_types is not None
