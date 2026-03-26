"""ADG importability contract for system_learning/types/pattern_analysis_types.py."""
from __future__ import annotations

def test_module_importable():
    """Module pattern_analysis_types must be importable."""
    import system_learning.types.pattern_analysis_types
    assert system_learning.types.pattern_analysis_types is not None