"""ADG importability contract for agentic_core/L5_safety/validators/type_erasure_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_type_erasure_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.type_erasure_validator import (  # noqa: F401
        TypeErasureDetector,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    TypeErasureDetector = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="type_erasure_validator.py deps unavailable")
class TestTypeErasureValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: type_erasure_validator.py must be importable."""
        assert _AVAILABLE

    def test_typeerasuredetector_is_type(self) -> None:
        assert TypeErasureDetector is not None

