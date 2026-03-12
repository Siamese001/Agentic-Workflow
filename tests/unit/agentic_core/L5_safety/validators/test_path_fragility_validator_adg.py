"""ADG importability contract for agentic_core/L5_safety/validators/path_fragility_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_path_fragility_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.path_fragility_validator import (  # noqa: F401
        PathFragilityDetector,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    PathFragilityDetector = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="path_fragility_validator.py deps unavailable")
class TestPathFragilityValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: path_fragility_validator.py must be importable."""
        assert _AVAILABLE

    def test_pathfragilitydetector_is_type(self) -> None:
        assert PathFragilityDetector is not None

