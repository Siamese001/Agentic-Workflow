"""ADG-driven tests for agentic_core/L0_routing/utils/project_root_util.py — fan_in=16.

16 modules depend on project root detection. Tests verify get_project_root,
get_validated_project_root, clear_project_root_cache, and PROJECT_ROOT_MARKERS.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


class TestGetProjectRoot:
    def test_returns_path_object(self):
        from agentic_core.L0_routing.utils.project_root_util import get_project_root
        result = get_project_root()
        assert isinstance(result, Path)

    def test_returns_existing_directory(self):
        from agentic_core.L0_routing.utils.project_root_util import get_project_root
        root = get_project_root()
        assert root.is_dir()

    def test_root_contains_agentic_core(self):
        from agentic_core.L0_routing.utils.project_root_util import get_project_root
        root = get_project_root()
        assert (root / "agentic_core").is_dir()

    def test_result_is_cached(self):
        from agentic_core.L0_routing.utils.project_root_util import get_project_root
        r1 = get_project_root()
        r2 = get_project_root()
        assert r1 == r2

    def test_accepts_explicit_start_path(self, tmp_path):
        from agentic_core.L0_routing.utils.project_root_util import (
            get_project_root,
            clear_project_root_cache,
        )
        # Starting from within the real repo should still find root
        clear_project_root_cache()
        root = get_project_root(str(Path(__file__).resolve()))
        assert root.is_dir()
        clear_project_root_cache()

    def test_raises_when_no_markers_found(self, tmp_path, monkeypatch):
        from agentic_core.L0_routing.utils.project_root_util import (
            get_project_root,
            clear_project_root_cache,
        )
        clear_project_root_cache()
        # A fresh tmp_path with no markers should raise
        isolated = tmp_path / "isolated" / "subdir"
        isolated.mkdir(parents=True)
        with pytest.raises(RuntimeError, match="Could not detect project root"):
            get_project_root(str(isolated))
        clear_project_root_cache()


class TestGetValidatedProjectRoot:
    def test_returns_path(self):
        from agentic_core.L0_routing.utils.project_root_util import get_validated_project_root
        result = get_validated_project_root()
        assert isinstance(result, Path)
        assert result.is_dir()

    def test_matches_get_project_root(self):
        from agentic_core.L0_routing.utils.project_root_util import (
            get_project_root,
            get_validated_project_root,
            clear_project_root_cache,
        )
        clear_project_root_cache()
        validated = get_validated_project_root()
        clear_project_root_cache()
        direct = get_project_root()
        assert validated == direct


class TestClearProjectRootCache:
    def test_cache_cleared_allows_fresh_resolution(self):
        from agentic_core.L0_routing.utils.project_root_util import (
            get_project_root,
            clear_project_root_cache,
        )
        r1 = get_project_root()
        clear_project_root_cache()
        r2 = get_project_root()
        assert r1 == r2  # same result, but re-computed

    def test_clear_does_not_raise(self):
        from agentic_core.L0_routing.utils.project_root_util import clear_project_root_cache
        clear_project_root_cache()
        clear_project_root_cache()  # idempotent


class TestProjectRootMarkers:
    def test_project_root_markers_is_frozenset(self):
        from agentic_core.L0_routing.utils.project_root_util import PROJECT_ROOT_MARKERS
        assert isinstance(PROJECT_ROOT_MARKERS, frozenset)

    def test_project_root_markers_contains_git(self):
        from agentic_core.L0_routing.utils.project_root_util import PROJECT_ROOT_MARKERS
        assert ".git" in PROJECT_ROOT_MARKERS

    def test_project_root_markers_contains_agentic_core(self):
        from agentic_core.L0_routing.utils.project_root_util import PROJECT_ROOT_MARKERS
        assert "agentic_core" in PROJECT_ROOT_MARKERS

    def test_root_markers_list_non_empty(self):
        from agentic_core.L0_routing.utils.project_root_util import ROOT_MARKERS
        assert isinstance(ROOT_MARKERS, list)
        assert len(ROOT_MARKERS) >= 2

    def test_all_exports_present(self):
        import agentic_core.L0_routing.utils.project_root_util as m
        for name in m.__all__:
            assert hasattr(m, name), f"Missing __all__ member: {name}"
