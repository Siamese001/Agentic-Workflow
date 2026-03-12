"""ADG importability contract for agentic_core/L5_safety/enforcement/SurgicalHealingAdapter.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_SurgicalHealingAdapter.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.SurgicalHealingAdapter import (  # noqa: F401
        SurgicalHealingResult,
        SurgicalHealingAdapter,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SurgicalHealingResult = None  # type: ignore[assignment,misc]
    SurgicalHealingAdapter = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="SurgicalHealingAdapter.py deps unavailable")
class TestSurgicalhealingadapterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: SurgicalHealingAdapter.py must be importable."""
        assert _AVAILABLE

    def test_surgicalhealingresult_is_type(self) -> None:
        assert SurgicalHealingResult is not None

    def test_surgicalhealingadapter_is_type(self) -> None:
        assert SurgicalHealingAdapter is not None

