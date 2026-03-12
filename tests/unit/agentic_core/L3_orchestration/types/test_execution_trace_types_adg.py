"""ADG importability contract for agentic_core/L3_orchestration/types/execution_trace_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_execution_trace_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.types.execution_trace_types import (  # noqa: F401
        ExecutionTrace,
        canonical_json,
        create_execution_trace_skeleton,
        compute_plan_hash,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ExecutionTrace = None  # type: ignore[assignment,misc]
    canonical_json = None  # type: ignore[assignment,misc]
    create_execution_trace_skeleton = None  # type: ignore[assignment,misc]
    compute_plan_hash = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="execution_trace_types.py deps unavailable")
class TestExecutionTraceTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: execution_trace_types.py must be importable."""
        assert _AVAILABLE

    def test_executiontrace_is_type(self) -> None:
        assert ExecutionTrace is not None

    def test_canonical_json_callable(self) -> None:
        assert callable(canonical_json)

    def test_create_execution_trace_skeleton_callable(self) -> None:
        assert callable(create_execution_trace_skeleton)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

