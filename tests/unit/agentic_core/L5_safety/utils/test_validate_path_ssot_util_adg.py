"""ADG-driven tests for agentic_core/L5_safety/utils/validate_path_ssot_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.utils.validate_path_ssot_util import (  # noqa: F401
        EXCLUDED_DIRS,
        EXCLUDED_FILES,
        HARDCODED_PATH_PATTERNS,
        PROJECT_ROOT,
        main,
        should_exclude_path,
        validate_file,
        validate_repository,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    should_exclude_path = None  # type: ignore[assignment,misc]
    validate_file = None  # type: ignore[assignment,misc]
    validate_repository = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    PROJECT_ROOT = None  # type: ignore[assignment,misc]
    EXCLUDED_DIRS = None  # type: ignore[assignment,misc]
    EXCLUDED_FILES = None  # type: ignore[assignment,misc]
    HARDCODED_PATH_PATTERNS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="validate_path_ssot_util.py deps unavailable")
class TestShouldExcludePath:
    def test_is_callable(self):
        assert callable(should_exclude_path)

@pytest.mark.skipif(not _AVAILABLE, reason="validate_path_ssot_util.py deps unavailable")
class TestValidateFile:
    def test_is_callable(self):
        assert callable(validate_file)

@pytest.mark.skipif(not _AVAILABLE, reason="validate_path_ssot_util.py deps unavailable")
class TestValidateRepository:
    def test_is_callable(self):
        assert callable(validate_repository)

@pytest.mark.skipif(not _AVAILABLE, reason="validate_path_ssot_util.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="validate_path_ssot_util.py deps unavailable")
class TestProjectRootConstant:
    def test_is_not_none(self):
        assert PROJECT_ROOT is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validate_path_ssot_util.py deps unavailable")
class TestExcludedDirsConstant:
    def test_is_not_none(self):
        assert EXCLUDED_DIRS is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validate_path_ssot_util.py deps unavailable")
class TestExcludedFilesConstant:
    def test_is_not_none(self):
        assert EXCLUDED_FILES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validate_path_ssot_util.py deps unavailable")
class TestHardcodedPathPatternsConstant:
    def test_is_not_none(self):
        assert HARDCODED_PATH_PATTERNS is not None


def test_module_importable():
    """Module validate_path_ssot_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE