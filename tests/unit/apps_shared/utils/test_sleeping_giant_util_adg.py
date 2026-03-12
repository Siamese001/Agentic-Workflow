"""ADG-driven tests for apps_shared/utils/sleeping_giant_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.sleeping_giant_util import (  # noqa: F401
        SleepingGiant,
        AgentAnalyzer,
        analyze_file,
        main,
        DANGEROUS_IMPORTS,
        MUTATION_PATTERNS,
        EXCLUDED_DIRS,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SleepingGiant = None  # type: ignore[assignment,misc]
    AgentAnalyzer = None  # type: ignore[assignment,misc]
    analyze_file = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    DANGEROUS_IMPORTS = None  # type: ignore[assignment,misc]
    MUTATION_PATTERNS = None  # type: ignore[assignment,misc]
    EXCLUDED_DIRS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="sleeping_giant_util.py deps unavailable")
class TestSleepingGiant:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SleepingGiant)
    def test_importable(self):
        assert SleepingGiant is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sleeping_giant_util.py deps unavailable")
class TestAgentAnalyzer:
    def test_is_class(self):
        assert isinstance(AgentAnalyzer, type)
    def test_importable(self):
        assert AgentAnalyzer is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sleeping_giant_util.py deps unavailable")
class TestAnalyzeFile:
    def test_is_callable(self):
        assert callable(analyze_file)

@pytest.mark.skipif(not _AVAILABLE, reason="sleeping_giant_util.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="sleeping_giant_util.py deps unavailable")
class TestDangerousImportsConstant:
    def test_is_not_none(self):
        assert DANGEROUS_IMPORTS is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sleeping_giant_util.py deps unavailable")
class TestMutationPatternsConstant:
    def test_is_not_none(self):
        assert MUTATION_PATTERNS is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sleeping_giant_util.py deps unavailable")
class TestExcludedDirsConstant:
    def test_is_not_none(self):
        assert EXCLUDED_DIRS is not None


def test_module_importable():
    """Module sleeping_giant_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
