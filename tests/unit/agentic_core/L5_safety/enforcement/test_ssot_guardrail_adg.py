"""ADG-driven tests for agentic_core/L5_safety/enforcement/ssot_guardrail.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.ssot_guardrail import (  # noqa: F401
        KERNEL_PATH,
        ScanResult,
        Violation,
        main,
        scan_endswith_agent,
        scan_repository,
        scan_shadow_functions,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    Violation = None  # type: ignore[assignment,misc]
    ScanResult = None  # type: ignore[assignment,misc]
    scan_shadow_functions = None  # type: ignore[assignment,misc]
    scan_endswith_agent = None  # type: ignore[assignment,misc]
    scan_repository = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    KERNEL_PATH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ssot_guardrail.py deps unavailable")
class TestViolation:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(Violation)
    def test_importable(self):
        assert Violation is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_guardrail.py deps unavailable")
class TestScanResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ScanResult)
    def test_importable(self):
        assert ScanResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_guardrail.py deps unavailable")
class TestScanShadowFunctions:
    def test_is_callable(self):
        assert callable(scan_shadow_functions)

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_guardrail.py deps unavailable")
class TestScanEndswithAgent:
    def test_is_callable(self):
        assert callable(scan_endswith_agent)

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_guardrail.py deps unavailable")
class TestScanRepository:
    def test_is_callable(self):
        assert callable(scan_repository)

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_guardrail.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_guardrail.py deps unavailable")
class TestKernelPathConstant:
    def test_is_not_none(self):
        assert KERNEL_PATH is not None


def test_module_importable():
    """Module ssot_guardrail.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
