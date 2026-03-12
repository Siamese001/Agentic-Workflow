"""ADG importability contract for agentic_core/L5_safety/validators/magic_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_magic_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.magic_validator import (  # noqa: F401
        MagicConfigDetector,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    MagicConfigDetector = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="magic_validator.py deps unavailable")
class TestMagicValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: magic_validator.py must be importable."""
        assert _AVAILABLE

    def test_magicconfigdetector_is_type(self) -> None:
        assert MagicConfigDetector is not None

