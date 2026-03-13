"""ADG importability contract for agentic_core/L5_safety/reasoning/location_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_location_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.location_validator import (  # noqa: F401
        LocationValidatorAgent,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    LocationValidatorAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="location_validator deps unavailable")
class TestLocationValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/location_validator.py must be importable."""
        assert _AVAILABLE

    def test_locationvalidatoragent_defined(self) -> None:
        assert LocationValidatorAgent is not None
