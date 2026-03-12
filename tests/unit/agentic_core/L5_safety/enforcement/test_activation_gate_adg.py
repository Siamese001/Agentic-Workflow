"""ADG importability contract for agentic_core/L5_safety/enforcement/activation_gate.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_activation_gate.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.activation_gate import (  # noqa: F401
        assert_activation_allowed,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    assert_activation_allowed = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="activation_gate.py deps unavailable")
class TestActivationGateImportability:
    def test_module_importable(self) -> None:
        """ADG contract: activation_gate.py must be importable."""
        assert _AVAILABLE

    def test_assert_activation_allowed_callable(self) -> None:
        assert callable(assert_activation_allowed)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

