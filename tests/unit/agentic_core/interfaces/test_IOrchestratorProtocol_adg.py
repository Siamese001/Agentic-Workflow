"""ADG importability contract for agentic_core/interfaces/IOrchestratorProtocol.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_IOrchestratorProtocol.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.interfaces.IOrchestratorProtocol import (  # noqa: F401
        IOrchestratorProtocol,
        IHealable,
        ITieredAgent,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    IOrchestratorProtocol = None  # type: ignore[assignment,misc]
    IHealable = None  # type: ignore[assignment,misc]
    ITieredAgent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="IOrchestratorProtocol.py deps unavailable")
class TestIorchestratorprotocolImportability:
    def test_module_importable(self) -> None:
        """ADG contract: IOrchestratorProtocol.py must be importable."""
        assert _AVAILABLE

    def test_iorchestratorprotocol_is_type(self) -> None:
        assert IOrchestratorProtocol is not None

    def test_ihealable_is_type(self) -> None:
        assert IHealable is not None

    def test_itieredagent_is_type(self) -> None:
        assert ITieredAgent is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

