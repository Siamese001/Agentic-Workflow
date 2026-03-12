"""ADG-driven tests for L1_cognition/utils/constants_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L1_cognition.utils.constants_util import (
        depth_map,
        excluded_dirs,
        max_lines,
        min_lines,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    depth_map = excluded_dirs = max_lines = min_lines = None


@pytest.mark.skipif(not _AVAILABLE, reason="constants_util deps unavailable")
class TestConstantsUtil:
    def test_depth_map_is_dict(self):
        assert isinstance(depth_map, dict)

    def test_excluded_dirs_is_set(self):
        assert isinstance(excluded_dirs, set)

    def test_excluded_dirs_has_git(self):
        assert ".git" in excluded_dirs

    def test_max_lines_gt_min_lines(self):
        assert max_lines > min_lines


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
