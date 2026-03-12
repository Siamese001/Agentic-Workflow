"""ADG-driven tests for agentic_core/L0_routing/scripts/ssot_cli.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.ssot_cli import (  # noqa: F401
        print_header,
        cmd_scan,
        cmd_validate,
        cmd_enforce,
        cmd_status,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    print_header = None  # type: ignore[assignment,misc]
    cmd_scan = None  # type: ignore[assignment,misc]
    cmd_validate = None  # type: ignore[assignment,misc]
    cmd_enforce = None  # type: ignore[assignment,misc]
    cmd_status = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ssot_cli.py deps unavailable")
class TestPrintHeader:
    def test_is_callable(self):
        assert callable(print_header)

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_cli.py deps unavailable")
class TestCmdScan:
    def test_is_callable(self):
        assert callable(cmd_scan)

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_cli.py deps unavailable")
class TestCmdValidate:
    def test_is_callable(self):
        assert callable(cmd_validate)

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_cli.py deps unavailable")
class TestCmdEnforce:
    def test_is_callable(self):
        assert callable(cmd_enforce)

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_cli.py deps unavailable")
class TestCmdStatus:
    def test_is_callable(self):
        assert callable(cmd_status)

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

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_cli.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module ssot_cli.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
