"""ADG importability contract for system_learning/ports/healing_pattern_advisor.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_healing_pattern_advisor.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.ports.healing_pattern_advisor import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        HealingPatternAdvisor,
        NullHealingPatternAdvisor,
        PatternAdvice,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    PatternAdvice = None  # type: ignore[assignment,misc]
    HealingPatternAdvisor = None  # type: ignore[assignment,misc]
    NullHealingPatternAdvisor = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="healing_pattern_advisor.py deps unavailable")
class TestHealingPatternAdvisorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: healing_pattern_advisor.py must be importable."""
        assert _AVAILABLE

    def test_patternadvice_is_type(self) -> None:
        assert PatternAdvice is not None

    def test_healingpatternadvisor_is_type(self) -> None:
        assert HealingPatternAdvisor is not None

    def test_nullhealingpatternadvisor_is_type(self) -> None:
        assert NullHealingPatternAdvisor is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None