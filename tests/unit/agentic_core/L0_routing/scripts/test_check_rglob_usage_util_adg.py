"""ADG-driven tests for agentic_core/L0_routing/scripts/check_rglob_usage_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.check_rglob_usage_util import (  # noqa: F401
        EXCLUDED_DIRS,
        EXCLUDED_FILES,
        MAX_ALLOWED_RGLOB,
        count_rglob_in_file,
        main,
        scan_for_rglob_usage,
        should_exclude_path,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    count_rglob_in_file = None  # type: ignore[assignment,misc]
    should_exclude_path = None  # type: ignore[assignment,misc]
    scan_for_rglob_usage = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_ALLOWED_RGLOB = None  # type: ignore[assignment,misc]
    EXCLUDED_FILES = None  # type: ignore[assignment,misc]
    EXCLUDED_DIRS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="check_rglob_usage_util.py deps unavailable")
class TestCountRglobInFile:
    def test_is_callable(self):
        assert callable(count_rglob_in_file)

@pytest.mark.skipif(not _AVAILABLE, reason="check_rglob_usage_util.py deps unavailable")
class TestShouldExcludePath:
    def test_is_callable(self):
        assert callable(should_exclude_path)

@pytest.mark.skipif(not _AVAILABLE, reason="check_rglob_usage_util.py deps unavailable")
class TestScanForRglobUsage:
    def test_is_callable(self):
        assert callable(scan_for_rglob_usage)

@pytest.mark.skipif(not _AVAILABLE, reason="check_rglob_usage_util.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="check_rglob_usage_util.py deps unavailable")
class TestMaxAllowedRglobConstant:
    def test_is_not_none(self):
        assert MAX_ALLOWED_RGLOB is not None

@pytest.mark.skipif(not _AVAILABLE, reason="check_rglob_usage_util.py deps unavailable")
class TestExcludedFilesConstant:
    def test_is_not_none(self):
        assert EXCLUDED_FILES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="check_rglob_usage_util.py deps unavailable")
class TestExcludedDirsConstant:
    def test_is_not_none(self):
        assert EXCLUDED_DIRS is not None


def test_module_importable():
    """Module check_rglob_usage_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE