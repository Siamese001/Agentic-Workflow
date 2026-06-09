"""Unit tests for apps_qna R1B advisory cache L4 integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from apps_qna.cache import r1b_semantic as mod


def test_r1b_l4_miss_remains_advisory() -> None:
    manager = MagicMock()
    manager.recall.return_value = None

    with patch.object(mod, "_get_semantic_cache_manager", return_value=manager):
        result = mod.r1b_lookup(
            interview_slug="runtime_root_senior",
            query_text="tell me about your platform architecture",
        )

    manager.recall.assert_called_once_with(
        "tell me about your platform architecture",
        "apps_qna.r1b_semantic",
        tenant_id="apps_qna",
        flow_class="R1B_READ",
    )
    assert result["advisory"] is True
    assert result["cache_hit"] is False
    assert result["cache_status"] == "miss"
    assert result["result"] is None
    assert result["suggestion"] is None


def test_r1b_l4_hit_is_suggestion_not_terminal_result() -> None:
    payload = {"answer": "cached coaching note", "confidence": 0.81}
    manager = MagicMock()
    manager.recall.return_value = payload

    with patch.object(mod, "_get_semantic_cache_manager", return_value=manager):
        result = mod.r1b_lookup(interview_slug="runtime_root_senior")

    manager.recall.assert_called_once_with(
        "runtime_root_senior",
        "apps_qna.r1b_semantic",
        tenant_id="apps_qna",
        flow_class="R1B_READ",
    )
    assert result["advisory"] is True
    assert result["cache_hit"] is True
    assert result["cache_status"] == "hit"
    assert result["confidence"] == 0.81
    assert result["result"] is None
    assert result["suggestion"] == payload


def test_r1b_l4_unavailable_degrades_to_advisory_miss() -> None:
    with patch.object(mod, "_get_semantic_cache_manager", side_effect=RuntimeError("offline")):
        result = mod.r1b_lookup(interview_slug="runtime_root_senior", query_text="question")

    assert result["advisory"] is True
    assert result["cache_hit"] is False
    assert result["cache_status"] == "unavailable"
    assert result["result"] is None
    assert result["suggestion"] is None


def test_r1b_empty_context_skips_l4_probe() -> None:
    with patch.object(mod, "_get_semantic_cache_manager") as get_manager:
        result = mod.r1b_lookup(interview_slug="", query_text=" ")

    get_manager.assert_not_called()
    assert result["advisory"] is True
    assert result["cache_status"] == "empty_context"
    assert result["result"] is None
