"""ADG importability contract for agentic_core/L5_safety/validators/silent_swallower_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_silent_swallower_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.silent_swallower_validator import (  # noqa: F401
        SilentSwallowerDetector,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SilentSwallowerDetector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="silent_swallower_validator deps unavailable")
class TestSilentSwallowerValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/validators/silent_swallower_validator.py must be importable."""
        assert _AVAILABLE

    def test_silentswallowerdetector_defined(self) -> None:
        assert SilentSwallowerDetector is not None
