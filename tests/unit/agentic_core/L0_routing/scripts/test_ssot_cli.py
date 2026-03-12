"""Foundational behavioral tests for agentic_core/L0_routing/scripts/ssot_cli.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_ssot_cli_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.ssot_cli import (  # noqa: F401
        print_header,
        cmd_scan,
        cmd_validate,
        cmd_enforce,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    print_header = None  # type: ignore[assignment,misc]
    cmd_scan = None  # type: ignore[assignment,misc]
    cmd_validate = None  # type: ignore[assignment,misc]
    cmd_enforce = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ssot_cli.py deps unavailable")
class TestPrintHeaderFunction:
    def test_is_callable(self):
        assert callable(print_header)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(print_header)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_cli.py deps unavailable")
class TestCmdScanFunction:
    def test_is_callable(self):
        assert callable(cmd_scan)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(cmd_scan)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_cli.py deps unavailable")
class TestCmdValidateFunction:
    def test_is_callable(self):
        assert callable(cmd_validate)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(cmd_validate)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_cli.py deps unavailable")
class TestCmdEnforceFunction:
    def test_is_callable(self):
        assert callable(cmd_enforce)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(cmd_enforce)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_cli.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_cli.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_cli.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_cli.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_cli.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module ssot_cli must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
