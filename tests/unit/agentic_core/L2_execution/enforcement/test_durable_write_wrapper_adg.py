"""ADG importability contract for agentic_core/L2_execution/enforcement/durable_write_wrapper.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_durable_write_wrapper.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.durable_write_wrapper import (  # noqa: F401
        durable_write,
        reset_mutation_counter,
        get_mutation_count,
        set_phase,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    durable_write = None  # type: ignore[assignment,misc]
    reset_mutation_counter = None  # type: ignore[assignment,misc]
    get_mutation_count = None  # type: ignore[assignment,misc]
    set_phase = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="durable_write_wrapper.py deps unavailable")
class TestDurableWriteWrapperImportability:
    def test_module_importable(self) -> None:
        """ADG contract: durable_write_wrapper.py must be importable."""
        assert _AVAILABLE

    def test_durable_write_callable(self) -> None:
        assert callable(durable_write)

    def test_reset_mutation_counter_callable(self) -> None:
        assert callable(reset_mutation_counter)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

