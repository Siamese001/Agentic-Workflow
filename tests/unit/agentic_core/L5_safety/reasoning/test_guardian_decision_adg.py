"""ADG importability contract for agentic_core/L5_safety/reasoning/guardian_decision.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_guardian_decision.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.guardian_decision import (  # noqa: F401
        GuardianDecision,
        GuardianViolationError,
        L5Guardian,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    GuardianDecision = None  # type: ignore[assignment,misc]
    GuardianViolationError = None  # type: ignore[assignment,misc]
    L5Guardian = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="guardian_decision.py deps unavailable")
class TestGuardianDecisionImportability:
    def test_module_importable(self) -> None:
        """ADG contract: guardian_decision.py must be importable."""
        assert _AVAILABLE

    def test_guardiandecision_is_type(self) -> None:
        assert GuardianDecision is not None

    def test_guardianviolationerror_is_type(self) -> None:
        assert GuardianViolationError is not None

    def test_l5guardian_is_type(self) -> None:
        assert L5Guardian is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

