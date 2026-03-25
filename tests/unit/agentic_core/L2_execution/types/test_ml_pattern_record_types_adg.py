"""ADG importability contract for agentic_core/L2_execution/types/ml_pattern_record_types.py."""
from __future__ import annotations

import agentic_core.L2_execution.types.ml_pattern_record_types  # noqa: F401


def test_module_importable():
    """Module ml_pattern_record_types must be importable."""
    assert agentic_core.L2_execution.types.ml_pattern_record_types is not None
