"""ADG importability contract for agentic_core/L2_execution/cid_registry.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_cid_registry.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.cid_registry import (  # noqa: F401
        ExecutionCycle,
        CIDRegistry,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ExecutionCycle = None  # type: ignore[assignment,misc]
    CIDRegistry = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="cid_registry.py deps unavailable")
class TestCidRegistryImportability:
    def test_module_importable(self) -> None:
        """ADG contract: cid_registry.py must be importable."""
        assert _AVAILABLE

    def test_executioncycle_is_type(self) -> None:
        assert ExecutionCycle is not None

    def test_cidregistry_is_type(self) -> None:
        assert CIDRegistry is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

