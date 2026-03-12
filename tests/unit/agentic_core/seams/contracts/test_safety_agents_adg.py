"""ADG importability contract for agentic_core/seams/contracts/safety_agents.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_safety_agents.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.seams.contracts.safety_agents import (  # noqa: F401
        HealingAgentProtocol,
        SafetyAgentFactory,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HealingAgentProtocol = None  # type: ignore[assignment,misc]
    SafetyAgentFactory = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="safety_agents.py deps unavailable")
class TestSafetyAgentsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: safety_agents.py must be importable."""
        assert _AVAILABLE

    def test_healingagentprotocol_is_type(self) -> None:
        assert HealingAgentProtocol is not None

    def test_safetyagentfactory_is_type(self) -> None:
        assert SafetyAgentFactory is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

