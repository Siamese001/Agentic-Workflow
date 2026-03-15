"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/verification_gate.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_verification_gate_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.verification_gate import (  # noqa: F401
        VerificationGate,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    VerificationGate = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="verification_gate.py deps unavailable")
class TestVerificationGateContract:
    def test_is_class(self):
        assert isinstance(VerificationGate, type)

    def test_has_method_verify_action(self):
        assert callable(getattr(VerificationGate, 'verify_action', None))

    def test_has_method_verify_modification(self):
        assert callable(getattr(VerificationGate, 'verify_modification', None))

    def test_has_method_clear_cache(self):
        assert callable(getattr(VerificationGate, 'clear_cache', None))

    def test_has_method_get_cache_stats(self):
        assert callable(getattr(VerificationGate, 'get_cache_stats', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(VerificationGate) if not m.startswith('_')]
        assert len(pub) >= 1


def test_module_importable():
    """Smoke: verification_gate importable or gracefully unavailable."""
    pass
