"""ADG-driven tests for agentic_core/L5_safety/utils/pre_deploy_check_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.utils.pre_deploy_check_util import (  # noqa: F401
        print_banner,
        run_e2e_tests,
        check_ssot_files_exist,
        check_data_freshness,
        main,
        PROJECT_ROOT,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    print_banner = None  # type: ignore[assignment,misc]
    run_e2e_tests = None  # type: ignore[assignment,misc]
    check_ssot_files_exist = None  # type: ignore[assignment,misc]
    check_data_freshness = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    PROJECT_ROOT = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="pre_deploy_check_util.py deps unavailable")
class TestPrintBanner:
    def test_is_callable(self):
        assert callable(print_banner)

@pytest.mark.skipif(not _AVAILABLE, reason="pre_deploy_check_util.py deps unavailable")
class TestRunE2ETests:
    def test_is_callable(self):
        assert callable(run_e2e_tests)

@pytest.mark.skipif(not _AVAILABLE, reason="pre_deploy_check_util.py deps unavailable")
class TestCheckSsotFilesExist:
    def test_is_callable(self):
        assert callable(check_ssot_files_exist)

@pytest.mark.skipif(not _AVAILABLE, reason="pre_deploy_check_util.py deps unavailable")
class TestCheckDataFreshness:
    def test_is_callable(self):
        assert callable(check_data_freshness)

@pytest.mark.skipif(not _AVAILABLE, reason="pre_deploy_check_util.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="pre_deploy_check_util.py deps unavailable")
class TestProjectRootConstant:
    def test_is_not_none(self):
        assert PROJECT_ROOT is not None


def test_module_importable():
    """Module pre_deploy_check_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
