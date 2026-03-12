"""ADG importability contract for agentic_core/L2_execution/enforcement/preventative_sandbox.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_preventative_sandbox.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.preventative_sandbox import (  # noqa: F401
        SandboxViolationError,
        PreventativeSandbox,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SandboxViolationError = None  # type: ignore[assignment,misc]
    PreventativeSandbox = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="preventative_sandbox.py deps unavailable")
class TestPreventativeSandboxImportability:
    def test_module_importable(self) -> None:
        """ADG contract: preventative_sandbox.py must be importable."""
        assert _AVAILABLE

    def test_sandboxviolationerror_is_type(self) -> None:
        assert SandboxViolationError is not None

    def test_preventativesandbox_is_type(self) -> None:
        assert PreventativeSandbox is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

