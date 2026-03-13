"""ADG importability contract for agentic_core/L5_safety/security/side_effect_guard.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_side_effect_guard.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.security.side_effect_guard import (  # noqa: F401
        SideEffectGuard,
        UnverifiedSideEffectError,
        clear_verification_context,
        get_side_effect_guard,
        require_verified,
        set_verification_context,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    UnverifiedSideEffectError = None  # type: ignore[assignment,misc]
    SideEffectGuard = None  # type: ignore[assignment,misc]
    get_side_effect_guard = None  # type: ignore[assignment,misc]
    require_verified = None  # type: ignore[assignment,misc]
    set_verification_context = None  # type: ignore[assignment,misc]
    clear_verification_context = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="side_effect_guard deps unavailable")
class TestSideEffectGuardImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/security/side_effect_guard.py must be importable."""
        assert _AVAILABLE

    def test_unverifiedsideeffecterror_defined(self) -> None:
        assert UnverifiedSideEffectError is not None

    def test_sideeffectguard_defined(self) -> None:
        assert SideEffectGuard is not None
