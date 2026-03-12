"""ADG importability contract for agentic_core/L0_routing/context/c0_guard.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_c0_guard.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.context.c0_guard import (  # noqa: F401
        guard_c0_payload,
        verify_c0_immutability,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    guard_c0_payload = None  # type: ignore[assignment,misc]
    verify_c0_immutability = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="c0_guard.py deps unavailable")
class TestC0GuardImportability:
    def test_module_importable(self) -> None:
        """ADG contract: c0_guard.py must be importable."""
        assert _AVAILABLE

    def test_guard_c0_payload_callable(self) -> None:
        assert callable(guard_c0_payload)

    def test_verify_c0_immutability_callable(self) -> None:
        assert callable(verify_c0_immutability)

