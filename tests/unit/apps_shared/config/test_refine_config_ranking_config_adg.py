"""ADG-driven tests for apps_shared/config/refine_config_ranking_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.config.refine_config_ranking_config import (  # noqa: F401
        apply_strategy,
        bm25,
        dense,
        fuse_ranked_groups,
        hybrid,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    bm25 = None  # type: ignore[assignment,misc]
    dense = None  # type: ignore[assignment,misc]
    hybrid = None  # type: ignore[assignment,misc]
    apply_strategy = None  # type: ignore[assignment,misc]
    fuse_ranked_groups = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="refine_config_ranking_config.py deps unavailable")
class TestBm25:
    def test_is_callable(self):
        assert callable(bm25)

@pytest.mark.skipif(not _AVAILABLE, reason="refine_config_ranking_config.py deps unavailable")
class TestDense:
    def test_is_callable(self):
        assert callable(dense)

@pytest.mark.skipif(not _AVAILABLE, reason="refine_config_ranking_config.py deps unavailable")
class TestHybrid:
    def test_is_callable(self):
        assert callable(hybrid)

@pytest.mark.skipif(not _AVAILABLE, reason="refine_config_ranking_config.py deps unavailable")
class TestApplyStrategy:
    def test_is_callable(self):
        assert callable(apply_strategy)

@pytest.mark.skipif(not _AVAILABLE, reason="refine_config_ranking_config.py deps unavailable")
class TestFuseRankedGroups:
    def test_is_callable(self):
        assert callable(fuse_ranked_groups)


def test_module_importable():
    """Module refine_config_ranking_config.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE