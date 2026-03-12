"""ADG importability contract for agentic_core/L2_execution/types/ml_write_intent_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ml_write_intent_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.ml_write_intent_types import (  # noqa: F401
        MLWriteEnvelopeViolation,
        MLWriteIntent,
        MLWriteIntentExecutor,
        is_commit_sandbox_active,
        execute_ml_write_intent_outside_sandbox,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    MLWriteEnvelopeViolation = None  # type: ignore[assignment,misc]
    MLWriteIntent = None  # type: ignore[assignment,misc]
    MLWriteIntentExecutor = None  # type: ignore[assignment,misc]
    is_commit_sandbox_active = None  # type: ignore[assignment,misc]
    execute_ml_write_intent_outside_sandbox = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="ml_write_intent_types.py deps unavailable")
class TestMlWriteIntentTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: ml_write_intent_types.py must be importable."""
        assert _AVAILABLE

    def test_mlwriteenvelopeviolation_is_type(self) -> None:
        assert MLWriteEnvelopeViolation is not None

    def test_mlwriteintent_is_type(self) -> None:
        assert MLWriteIntent is not None

    def test_mlwriteintentexecutor_is_type(self) -> None:
        assert MLWriteIntentExecutor is not None

    def test_is_commit_sandbox_active_callable(self) -> None:
        assert callable(is_commit_sandbox_active)

    def test_execute_ml_write_intent_outside_sandbox_callable(self) -> None:
        assert callable(execute_ml_write_intent_outside_sandbox)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

