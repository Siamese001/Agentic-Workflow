"""ADG importability contract for system_learning/ports/healing_pattern_advisor.py."""
from __future__ import annotations

def test_module_importable():
    """Module healing_pattern_advisor must be importable."""
    import system_learning.ports.healing_pattern_advisor
    assert system_learning.ports.healing_pattern_advisor is not None