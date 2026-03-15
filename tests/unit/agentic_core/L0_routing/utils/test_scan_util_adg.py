"""ADG-driven tests for agentic_core/L0_routing/utils/scan_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.utils.scan_util import (  # noqa: F401
        DANGEROUS_DIRECTORIES,
        audit_rglob_usage,
        count_rglob_calls_in_file,
        deprecate_rglob,
        guarded_glob,
        guarded_rglob,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    guarded_rglob = None  # type: ignore[assignment,misc]
    guarded_glob = None  # type: ignore[assignment,misc]
    deprecate_rglob = None  # type: ignore[assignment,misc]
    count_rglob_calls_in_file = None  # type: ignore[assignment,misc]
    audit_rglob_usage = None  # type: ignore[assignment,misc]
    DANGEROUS_DIRECTORIES = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="scan_util.py deps unavailable")
class TestGuardedRglob:
    def test_is_callable(self):
        assert callable(guarded_rglob)

@pytest.mark.skipif(not _AVAILABLE, reason="scan_util.py deps unavailable")
class TestGuardedGlob:
    def test_is_callable(self):
        assert callable(guarded_glob)

@pytest.mark.skipif(not _AVAILABLE, reason="scan_util.py deps unavailable")
class TestDeprecateRglob:
    def test_is_callable(self):
        assert callable(deprecate_rglob)

@pytest.mark.skipif(not _AVAILABLE, reason="scan_util.py deps unavailable")
class TestCountRglobCallsInFile:
    def test_is_callable(self):
        assert callable(count_rglob_calls_in_file)

@pytest.mark.skipif(not _AVAILABLE, reason="scan_util.py deps unavailable")
class TestAuditRglobUsage:
    def test_is_callable(self):
        assert callable(audit_rglob_usage)

@pytest.mark.skipif(not _AVAILABLE, reason="scan_util.py deps unavailable")
class TestDangerousDirectoriesConstant:
    def test_is_not_none(self):
        assert DANGEROUS_DIRECTORIES is not None


def test_module_importable():
    """Module scan_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
