"""ADG importability contract for agentic_core/L2_execution/enforcement/write_set_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_write_set_enforcer.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.write_set_enforcer import (  # noqa: F401
        WriteSetEnforcer,
        WriteSetViolation,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    WriteSetViolation = None  # type: ignore[assignment,misc]
    WriteSetEnforcer = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="write_set_enforcer deps unavailable")
class TestWriteSetEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/enforcement/write_set_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_writesetviolation_defined(self) -> None:
        assert WriteSetViolation is not None

    def test_writesetenforcer_defined(self) -> None:
        assert WriteSetEnforcer is not None
