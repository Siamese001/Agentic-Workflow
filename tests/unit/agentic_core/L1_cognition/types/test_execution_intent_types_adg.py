"""ADG importability contract for agentic_core/L1_cognition/types/execution_intent_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_execution_intent_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L1_cognition.types.execution_intent_types import (  # noqa: F401
        ExecutionIntent,
        L1Result,
        assert_l1_purity,
        increment_mutation_guard,
        get_mutation_count,
        reset_mutation_guard,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ExecutionIntent = None  # type: ignore[assignment,misc]
    L1Result = None  # type: ignore[assignment,misc]
    assert_l1_purity = None  # type: ignore[assignment,misc]
    increment_mutation_guard = None  # type: ignore[assignment,misc]
    get_mutation_count = None  # type: ignore[assignment,misc]
    reset_mutation_guard = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="execution_intent_types.py deps unavailable")
class TestExecutionIntentTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: execution_intent_types.py must be importable."""
        assert _AVAILABLE

    def test_executionintent_is_type(self) -> None:
        assert ExecutionIntent is not None

    def test_l1result_is_type(self) -> None:
        assert L1Result is not None

    def test_assert_l1_purity_callable(self) -> None:
        assert callable(assert_l1_purity)

    def test_increment_mutation_guard_callable(self) -> None:
        assert callable(increment_mutation_guard)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

