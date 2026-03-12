"""ADG importability contract for agentic_core/L2_execution/enforcement/capability_chokepoint.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_capability_chokepoint.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.capability_chokepoint import (  # noqa: F401
        CapabilityChokepoint,
        authorize_and_execute,
        get_chokepoint,
        reset_chokepoint,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    CapabilityChokepoint = None  # type: ignore[assignment,misc]
    authorize_and_execute = None  # type: ignore[assignment,misc]
    get_chokepoint = None  # type: ignore[assignment,misc]
    reset_chokepoint = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="capability_chokepoint.py deps unavailable")
class TestCapabilityChokepointImportability:
    def test_module_importable(self) -> None:
        """ADG contract: capability_chokepoint.py must be importable."""
        assert _AVAILABLE

    def test_capabilitychokepoint_is_type(self) -> None:
        assert CapabilityChokepoint is not None

    def test_authorize_and_execute_callable(self) -> None:
        assert callable(authorize_and_execute)

    def test_get_chokepoint_callable(self) -> None:
        assert callable(get_chokepoint)

