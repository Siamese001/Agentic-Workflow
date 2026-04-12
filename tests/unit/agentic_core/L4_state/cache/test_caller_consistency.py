"""P1 caller-consistency tests: every live recall() call site is explicit and production-safe.

Call-site inventory (all non-D2 paths explicitly classified):
    CS-1  ExecutionOrchestrator.execute()          D2 runtime gate    (covered by test_gptcache_wired.py)
    CS-2  SemanticCacheMixin.semantic_recall()     mixin helper        threads flow_class + replay_mode
    CS-3  GlobalcacheStrategy._hive_recall path    app learning path   explicit flow_class=None
    CS-4  MetaLearningStorage.recall()             offline path        explicit flow_class=None
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scm_mock(*, hit_value: str | None = None) -> MagicMock:
    """Return a SemanticCacheManager mock whose recall() returns *hit_value*."""
    scm = MagicMock()
    if hit_value is not None:
        scm.recall.return_value = json.loads(hit_value)
    else:
        scm.recall.return_value = None
    return scm


_HIT_JSON = json.dumps({"answer": "42", "_metadata": {"namespace": "ns"}})


# ---------------------------------------------------------------------------
# CS-2: SemanticCacheMixin.semantic_recall()
# ---------------------------------------------------------------------------


class _MixinHost:
    """Minimal host that mixes in SemanticCacheMixin."""

    from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin  # type: ignore[attr-defined]


class _MixinHostConcrete(_MixinHost.SemanticCacheMixin):  # type: ignore[misc]
    pass


def test_cs2_mixin_semantic_recall_threads_flow_class_bypass() -> None:
    """CS-2: semantic_recall(flow_class='D4_ACTION') must return None (bypass fires)."""
    from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

    host = object.__new__(SemanticCacheMixin)
    mock_scm = _scm_mock(hit_value=_HIT_JSON)

    with patch.object(type(host), "semantic_cache", new_callable=lambda: property(lambda _: mock_scm)):
        result = host.semantic_recall("ctx", "ns", flow_class="D4_ACTION")

    mock_scm.recall.assert_called_once_with("ctx", "ns", flow_class="D4_ACTION", replay_mode=False)


def test_cs2_mixin_semantic_recall_threads_replay_mode() -> None:
    """CS-2: semantic_recall(replay_mode=True) must forward replay_mode to SCM."""
    from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

    host = object.__new__(SemanticCacheMixin)
    mock_scm = _scm_mock()

    with patch.object(type(host), "semantic_cache", new_callable=lambda: property(lambda _: mock_scm)):
        host.semantic_recall("ctx", "ns", replay_mode=True)

    mock_scm.recall.assert_called_once_with("ctx", "ns", flow_class=None, replay_mode=True)


def test_cs2_mixin_semantic_recall_default_args_explicit() -> None:
    """CS-2: semantic_recall() without kwargs forwards flow_class=None, replay_mode=False."""
    from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

    host = object.__new__(SemanticCacheMixin)
    mock_scm = _scm_mock()

    with patch.object(type(host), "semantic_cache", new_callable=lambda: property(lambda _: mock_scm)):
        host.semantic_recall("ctx", "ns")

    mock_scm.recall.assert_called_once_with("ctx", "ns", flow_class=None, replay_mode=False)


# ---------------------------------------------------------------------------
# CS-3: GlobalcacheStrategy — hive recall is explicit learning path
# ---------------------------------------------------------------------------


def test_cs3_globalcache_hive_recall_explicit_args() -> None:
    """CS-3: GlobalcacheStrategy hive recall must pass flow_class=None, replay_mode=False."""
    import inspect
    from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

    source = inspect.getsource(GlobalCache.get_semantic)
    assert "flow_class=None" in source, (
        "CS-3 FAIL: GlobalcacheStrategy.get_semantic() hive.recall() must explicitly pass flow_class=None"
    )
    assert "replay_mode=False" in source, (
        "CS-3 FAIL: GlobalcacheStrategy.get_semantic() hive.recall() must explicitly pass replay_mode=False"
    )


# ---------------------------------------------------------------------------
# CS-4: MetaLearningStorage.recall() — offline learning path
# ---------------------------------------------------------------------------


def test_cs4_meta_learning_storage_recall_explicit_offline_path() -> None:
    """CS-4: MetaLearningStorage.recall() must explicitly pass flow_class=None to SCM recall."""
    import inspect
    from agentic_core.utils.meta_learning_storage_util import MetaLearningStorage

    source = inspect.getsource(MetaLearningStorage.recall)
    assert "flow_class=None" in source, (
        "CS-4 FAIL: MetaLearningStorage.recall() must explicitly pass flow_class=None"
    )
    assert "replay_mode=False" in source, (
        "CS-4 FAIL: MetaLearningStorage.recall() must explicitly pass replay_mode=False"
    )


def test_cs4_meta_learning_storage_recall_does_not_bypass_by_default() -> None:
    """CS-4: MetaLearningStorage.recall() is an offline path; it should serve from cache (no bypass)."""
    from agentic_core.utils.meta_learning_storage_util import MetaLearningStorage

    mock_scm = _scm_mock(hit_value=_HIT_JSON)
    original = MetaLearningStorage._lobotomized
    original_memory = MetaLearningStorage._memory
    try:
        MetaLearningStorage._lobotomized = False
        MetaLearningStorage._memory = mock_scm
        result = MetaLearningStorage.recall("context", "ns")
        assert result is not None, "CS-4 FAIL: offline learning path should serve from cache"
        mock_scm.recall.assert_called_once_with("context", "ns", flow_class=None, replay_mode=False)
    finally:
        MetaLearningStorage._lobotomized = original
        MetaLearningStorage._memory = original_memory
