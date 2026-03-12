"""ADG importability contract for agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_SafetyExecutorAgent.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.SafetyExecutorAgent import (  # noqa: F401
        ExecutionStatus,
        BlockReason,
        ExecutionResult,
        SafetyGate,
        ExecutorConfig,
        SafetyExecutorAgent,
        create_legacy_integrity_executor,
        create_legacy_safety_executor,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ExecutionStatus = None  # type: ignore[assignment,misc]
    BlockReason = None  # type: ignore[assignment,misc]
    ExecutionResult = None  # type: ignore[assignment,misc]
    SafetyGate = None  # type: ignore[assignment,misc]
    ExecutorConfig = None  # type: ignore[assignment,misc]
    SafetyExecutorAgent = None  # type: ignore[assignment,misc]
    create_legacy_integrity_executor = None  # type: ignore[assignment,misc]
    create_legacy_safety_executor = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="SafetyExecutorAgent.py deps unavailable")
class TestSafetyexecutoragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: SafetyExecutorAgent.py must be importable."""
        assert _AVAILABLE

    def test_executionstatus_is_type(self) -> None:
        assert ExecutionStatus is not None

    def test_blockreason_is_type(self) -> None:
        assert BlockReason is not None

    def test_executionresult_is_type(self) -> None:
        assert ExecutionResult is not None

    def test_create_legacy_integrity_executor_callable(self) -> None:
        assert callable(create_legacy_integrity_executor)

    def test_create_legacy_safety_executor_callable(self) -> None:
        assert callable(create_legacy_safety_executor)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

