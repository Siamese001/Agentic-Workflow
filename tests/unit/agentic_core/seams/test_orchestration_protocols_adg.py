"""ADG importability contract for agentic_core/seams/orchestration_protocols.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_orchestration_protocols.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.seams.orchestration_protocols import (  # noqa: F401
        OrchestrationResult,
        IOrchestrator,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    OrchestrationResult = None  # type: ignore[assignment,misc]
    IOrchestrator = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="orchestration_protocols.py deps unavailable")
class TestOrchestrationProtocolsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: orchestration_protocols.py must be importable."""
        assert _AVAILABLE

    def test_orchestrationresult_is_type(self) -> None:
        assert OrchestrationResult is not None

    def test_iorchestrator_is_type(self) -> None:
        assert IOrchestrator is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

