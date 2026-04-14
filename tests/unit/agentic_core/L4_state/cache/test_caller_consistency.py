"""P1 caller-consistency tests for semantic-cache recall call sites.

Call-site inventory (all non-D2 paths explicitly classified):
    CS-1  ExecutionOrchestrator.execute()          D2 runtime gate    (covered by test_gptcache_wired.py)
    CS-2  SemanticCacheMixin.semantic_recall()     mixin helper        threads flow_class + replay_mode
    CS-3  GlobalcacheStrategy._hive_recall path    app learning path   explicit flow_class=None
    CS-4  MetaLearningStorage.recall()             offline path        explicit flow_class=None
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from import_helpers import ensure_project_root, import_or_skip

ensure_project_root(__file__)
_semantic_cache_mixin_module = import_or_skip(
    "agentic_core.mixins.semantic_cache_mixin",
    reason="SemanticCacheMixin unavailable for caller-consistency tests",
)
_meta_learning_module = import_or_skip(
    "agentic_core.utils.meta_learning_storage_util",
    reason="MetaLearningStorage unavailable for caller-consistency tests",
)
SemanticCacheMixin = _semantic_cache_mixin_module.SemanticCacheMixin
MetaLearningStorage = _meta_learning_module.MetaLearningStorage


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scm_mock(*, hit_value: str | None = None) -> MagicMock:
    """Return a SemanticCacheManager mock whose recall() returns *hit_value*."""
    scm = MagicMock()
    scm.recall.return_value = json.loads(hit_value) if hit_value is not None else None
    return scm


_HIT_JSON = json.dumps({"answer": "42", "_metadata": {"namespace": "ns"}})


# ---------------------------------------------------------------------------
# CS-2: SemanticCacheMixin.semantic_recall()
# ---------------------------------------------------------------------------


def _new_mixin_host() -> SemanticCacheMixin:
    """Allocate a bare SemanticCacheMixin instance without invoking project constructors."""
    return object.__new__(SemanticCacheMixin)


def test_cs2_mixin_semantic_recall_threads_flow_class_bypass() -> None:
    """CS-2: semantic_recall(flow_class='D4_ACTION') must forward the explicit flow class."""
    host = _new_mixin_host()
    mock_scm = _scm_mock(hit_value=_HIT_JSON)

    with patch.object(type(host), "semantic_cache", new_callable=lambda: property(lambda _: mock_scm)):
        result = host.semantic_recall("ctx", "ns", flow_class="D4_ACTION")

    mock_scm.recall.assert_called_once_with("ctx", "ns", flow_class="D4_ACTION", replay_mode=False)
    assert result == mock_scm.recall.return_value, (
        "CS-2 FAIL: semantic_recall() must propagate SCM.recall() return value"
    )


def test_cs2_mixin_semantic_recall_threads_replay_mode() -> None:
    """CS-2: semantic_recall(replay_mode=True) must forward replay_mode to SCM."""
    host = _new_mixin_host()
    mock_scm = _scm_mock()

    with patch.object(type(host), "semantic_cache", new_callable=lambda: property(lambda _: mock_scm)):
        result = host.semantic_recall("ctx", "ns", replay_mode=True)

    mock_scm.recall.assert_called_once_with("ctx", "ns", flow_class=None, replay_mode=True)
    assert result is None, "CS-2 FAIL: semantic_recall(replay_mode=True) must propagate None from SCM"


def test_cs2_mixin_semantic_recall_default_args_explicit() -> None:
    """CS-2: semantic_recall() without kwargs forwards flow_class=None, replay_mode=False."""
    host = _new_mixin_host()
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

    globalcache_module = pytest.importorskip(
        "apps_shared.enforcement.GlobalcacheStrategy",
        reason="GlobalcacheStrategy unavailable for caller-consistency tests",
    )
    source = inspect.getsource(globalcache_module.GlobalCache.get_semantic)
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

    source = inspect.getsource(MetaLearningStorage.recall)
    assert "flow_class=None" in source, (
        "CS-4 FAIL: MetaLearningStorage.recall() must explicitly pass flow_class=None"
    )
    assert "replay_mode=False" in source, (
        "CS-4 FAIL: MetaLearningStorage.recall() must explicitly pass replay_mode=False"
    )


def test_cs4_meta_learning_storage_recall_lobotomized_returns_none() -> None:
    """CS-4 failure path: recall() must return None immediately when _lobotomized=True."""
    mock_scm = _scm_mock(hit_value=_HIT_JSON)
    original_lob = MetaLearningStorage._lobotomized
    original_mem = MetaLearningStorage._memory
    try:
        MetaLearningStorage._lobotomized = True
        MetaLearningStorage._memory = mock_scm
        result = MetaLearningStorage.recall("context", "ns")
        assert result is None, "CS-4 FAIL: lobotomized path must return None"
        mock_scm.recall.assert_not_called()
    finally:
        MetaLearningStorage._lobotomized = original_lob
        MetaLearningStorage._memory = original_mem


def test_cs4_meta_learning_storage_recall_exception_returns_none() -> None:
    """CS-4 failure path: when SCM.recall() raises, recall() must swallow and return None."""
    mock_scm = MagicMock()
    mock_scm.recall.side_effect = RuntimeError("simulated SCM error")
    original_lob = MetaLearningStorage._lobotomized
    original_mem = MetaLearningStorage._memory
    try:
        MetaLearningStorage._lobotomized = False
        MetaLearningStorage._memory = mock_scm
        result = MetaLearningStorage.recall("context", "ns")
        assert result is None, "CS-4 FAIL: exception path must return None"
        mock_scm.recall.assert_called_once_with("context", "ns", flow_class=None, replay_mode=False)
    finally:
        MetaLearningStorage._lobotomized = original_lob
        MetaLearningStorage._memory = original_mem


def test_cs4_meta_learning_storage_recall_does_not_bypass_by_default() -> None:
    """CS-4: MetaLearningStorage.recall() is an offline path; it should serve from cache."""
    mock_scm = _scm_mock(hit_value=_HIT_JSON)
    original_lob = MetaLearningStorage._lobotomized
    original_mem = MetaLearningStorage._memory
    try:
        MetaLearningStorage._lobotomized = False
        MetaLearningStorage._memory = mock_scm
        result = MetaLearningStorage.recall("context", "ns")
        assert result is not None, "CS-4 FAIL: offline learning path should serve from cache"
        mock_scm.recall.assert_called_once_with("context", "ns", flow_class=None, replay_mode=False)
    finally:
        MetaLearningStorage._lobotomized = original_lob
        MetaLearningStorage._memory = original_mem
