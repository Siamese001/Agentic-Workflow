"""ADG importability contract for system_learning/types/pattern_analysis_types.py."""
from __future__ import annotations

import system_learning.types.pattern_analysis_types  # noqa: F401


def test_module_importable():
    """Module pattern_analysis_types must be importable."""
    assert system_learning.types.pattern_analysis_types is not None
