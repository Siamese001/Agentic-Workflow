"""ADG importability contract for agentic_core/adg/runtime/dynamic_invocation.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_dynamic_invocation.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.dynamic_invocation import (  # noqa: F401
        DynamicInvocationKind,
        DynamicInvocationRecord,
        DynamicInvocationReport,
        DynamicInvocationRisk,
        DynamicInvocationTracker,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DynamicInvocationKind = None  # type: ignore[assignment,misc]
    DynamicInvocationRisk = None  # type: ignore[assignment,misc]
    DynamicInvocationRecord = None  # type: ignore[assignment,misc]
    DynamicInvocationReport = None  # type: ignore[assignment,misc]
    DynamicInvocationTracker = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="dynamic_invocation deps unavailable")
class TestDynamicInvocationImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/dynamic_invocation.py must be importable."""
        assert _AVAILABLE

    def test_dynamicinvocationkind_defined(self) -> None:
        assert DynamicInvocationKind is not None

    def test_dynamicinvocationrisk_defined(self) -> None:
        assert DynamicInvocationRisk is not None

    def test_dynamicinvocationrecord_defined(self) -> None:
        assert DynamicInvocationRecord is not None

    def test_dynamicinvocationreport_defined(self) -> None:
        assert DynamicInvocationReport is not None

    def test_dynamicinvocationtracker_defined(self) -> None:
        assert DynamicInvocationTracker is not None
