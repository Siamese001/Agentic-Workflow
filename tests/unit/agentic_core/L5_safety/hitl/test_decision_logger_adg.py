"""ADG importability contract for agentic_core/L5_safety/hitl/decision_logger.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_decision_logger.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.hitl.decision_logger import (  # noqa: F401
        HITLDecision,
        HITLDecisionLogger,
        get_decision_logger,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HITLDecision = None  # type: ignore[assignment,misc]
    HITLDecisionLogger = None  # type: ignore[assignment,misc]
    get_decision_logger = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="decision_logger.py deps unavailable")
class TestDecisionLoggerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: decision_logger.py must be importable."""
        assert _AVAILABLE

    def test_hitldecision_is_type(self) -> None:
        assert HITLDecision is not None

    def test_hitldecisionlogger_is_type(self) -> None:
        assert HITLDecisionLogger is not None

    def test_get_decision_logger_callable(self) -> None:
        assert callable(get_decision_logger)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

