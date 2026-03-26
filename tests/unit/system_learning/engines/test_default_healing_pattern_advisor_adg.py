"""ADG importability contract for system_learning/engines/default_healing_pattern_advisor.py."""
from __future__ import annotations



def test_module_importable():
    """Module default_healing_pattern_advisor must be importable."""
    import system_learning.engines.default_healing_pattern_advisor  # noqa: F401

    assert system_learning.engines.default_healing_pattern_advisor is not None
