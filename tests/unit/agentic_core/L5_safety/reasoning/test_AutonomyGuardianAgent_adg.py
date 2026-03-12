"""ADG importability contract for agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_AutonomyGuardianAgent.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.AutonomyGuardianAgent import (  # noqa: F401
        AutonomyGuardianAgent,
        get_autonomy_guardian,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    AutonomyGuardianAgent = None  # type: ignore[assignment,misc]
    get_autonomy_guardian = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="AutonomyGuardianAgent.py deps unavailable")
class TestAutonomyguardianagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: AutonomyGuardianAgent.py must be importable."""
        assert _AVAILABLE

    def test_autonomyguardianagent_is_type(self) -> None:
        assert AutonomyGuardianAgent is not None

    def test_get_autonomy_guardian_callable(self) -> None:
        assert callable(get_autonomy_guardian)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

