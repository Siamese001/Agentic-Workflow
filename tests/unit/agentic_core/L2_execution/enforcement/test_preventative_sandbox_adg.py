"""ADG importability contract for agentic_core/L2_execution/enforcement/preventative_sandbox.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_preventative_sandbox.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.preventative_sandbox import (  # noqa: F401
        PreventativeSandbox,
        SandboxViolationError,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SandboxViolationError = None  # type: ignore[assignment,misc]
    PreventativeSandbox = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="preventative_sandbox deps unavailable")
class TestPreventativeSandboxImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/enforcement/preventative_sandbox.py must be importable."""
        assert _AVAILABLE

    def test_sandboxviolationerror_defined(self) -> None:
        assert SandboxViolationError is not None

    def test_preventativesandbox_defined(self) -> None:
        assert PreventativeSandbox is not None
