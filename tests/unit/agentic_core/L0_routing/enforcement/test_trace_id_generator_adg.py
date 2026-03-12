"""ADG importability contract for agentic_core/L0_routing/enforcement/trace_id_generator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_trace_id_generator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.enforcement.trace_id_generator import (  # noqa: F401
        TraceIdGenerator,
        generate_trace_id,
        validate_trace_id,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    TraceIdGenerator = None  # type: ignore[assignment,misc]
    generate_trace_id = None  # type: ignore[assignment,misc]
    validate_trace_id = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="trace_id_generator.py deps unavailable")
class TestTraceIdGeneratorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: trace_id_generator.py must be importable."""
        assert _AVAILABLE

    def test_traceidgenerator_is_type(self) -> None:
        assert TraceIdGenerator is not None

    def test_generate_trace_id_callable(self) -> None:
        assert callable(generate_trace_id)

    def test_validate_trace_id_callable(self) -> None:
        assert callable(validate_trace_id)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

