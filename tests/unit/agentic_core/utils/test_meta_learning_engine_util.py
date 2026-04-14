"""Tests for agentic_core/utils/meta_learning_engine_util.py hardening changes."""

from __future__ import annotations


def test_schedule_learn_task_no_loop_returns_silently():
    """_schedule_learn_task with no running event loop returns None without raising."""
    from agentic_core.utils.meta_learning_engine_util import _schedule_learn_task

    _schedule_learn_task("test_agent", "some_context", {"key": "value"})  # must not raise


def test_discover_agent_context_no_kg_bridge_returns_empty_dict():
    """discover_agent_context returns {} when _kg_bridge is None (bridge unavailable)."""
    from agentic_core.utils.meta_learning_engine_util import MetaLearningEngine

    old_bridge = MetaLearningEngine._kg_bridge
    try:
        MetaLearningEngine._kg_bridge = None
        result = MetaLearningEngine.discover_agent_context("test_agent")
        assert result == {}
    finally:
        MetaLearningEngine._kg_bridge = old_bridge


def test_recall_or_execute_lobotomized_calls_fn_directly():
    """When _lobotomized is True, recall_or_execute calls execution_fn directly without memory lookup."""
    from agentic_core.utils.meta_learning_engine_util import MetaLearningEngine, MetaLearningStorage

    old_flag = MetaLearningStorage._lobotomized
    try:
        MetaLearningStorage._lobotomized = True
        result = MetaLearningEngine.recall_or_execute("test_agent", "ctx", lambda: "direct_result")
        assert result == "direct_result"
    finally:
        MetaLearningStorage._lobotomized = old_flag
