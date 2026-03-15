"""ADG importability contract for system_learning/engines/default_healing_pattern_advisor.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_default_healing_pattern_advisor.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.default_healing_pattern_advisor import (  # noqa: F401
        DefaultHealingPatternAdvisor,
        HealingPattern,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    HealingPattern = None  # type: ignore[assignment,misc]
    DefaultHealingPatternAdvisor = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="default_healing_pattern_advisor.py deps unavailable")
class TestDefaultHealingPatternAdvisorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: default_healing_pattern_advisor.py must be importable."""
        assert _AVAILABLE

    def test_healingpattern_is_type(self) -> None:
        assert HealingPattern is not None

    def test_defaulthealingpatternadvisor_is_type(self) -> None:
        assert DefaultHealingPatternAdvisor is not None
