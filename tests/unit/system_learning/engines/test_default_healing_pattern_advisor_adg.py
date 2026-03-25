"""ADG importability contract for system_learning/engines/default_healing_pattern_advisor.py."""
from __future__ import annotations

import system_learning.engines.default_healing_pattern_advisor  # noqa: F401


def test_module_importable():
    """Module default_healing_pattern_advisor must be importable."""
    assert system_learning.engines.default_healing_pattern_advisor is not None
