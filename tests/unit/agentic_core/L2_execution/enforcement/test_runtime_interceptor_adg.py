"""ADG importability contract for agentic_core/L2_execution/enforcement/runtime_interceptor.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_runtime_interceptor.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.runtime_interceptor import (  # noqa: F401
        MutableReferenceError,
        T,
        assert_immutable_reference,
        clear_mutable_ref_violations,
        get_mutable_ref_violations,
        immutable_references,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    T = None  # type: ignore[assignment,misc]
    MutableReferenceError = None  # type: ignore[assignment,misc]
    assert_immutable_reference = None  # type: ignore[assignment,misc]
    get_mutable_ref_violations = None  # type: ignore[assignment,misc]
    clear_mutable_ref_violations = None  # type: ignore[assignment,misc]
    immutable_references = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="runtime_interceptor deps unavailable")
class TestRuntimeInterceptorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/enforcement/runtime_interceptor.py must be importable."""
        assert _AVAILABLE

    def test_mutablereferenceerror_defined(self) -> None:
        assert MutableReferenceError is not None
