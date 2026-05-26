"""Regression: unify_bullets SC paths must append PATH_FRAMING (not ibm_bullets)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

# Import graph evidence before bullet_lane pulls provider stack (conftest may preload shims).
from apps_rg.runtime.sections.unify_bullets_graph_evidence import append_unify_path_framing_to_messages


def test_append_unify_path_framing_is_pure_on_empty_messages() -> None:
    assert append_unify_path_framing_to_messages([], path_index=0, temperature=0.5) == []


def test_unify_sc_paths_append_path_framing_per_call() -> None:
    from apps_rg.runtime.providers.qwen_vllm_provider import ProviderResult
    from apps_rg.runtime.reasoning.bullet_lane_self_consistency import run_qwen_self_consistency_paths

    seen_messages: list[list[dict]] = []

    def _stub(payload: dict, **_: object) -> ProviderResult:
        seen_messages.append(list(payload.get("messages") or []))
        return ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model="m",
            raw_model_output='{"bullets":[]}',
            provider_response={},
        )

    with patch(
        "apps_rg.runtime.reasoning.bullet_lane_self_consistency.call_qwen_vllm",
        side_effect=_stub,
    ):
        paths, _ = run_qwen_self_consistency_paths(
            section_lane="unify_bullets",
            provider_payload={"model": "m", "messages": [{"role": "user", "content": "base"}]},
            parse_model_json=lambda _r: (None, ""),
            path_count=2,
        )

    assert len(paths) == 2
    assert len(seen_messages) == 2
    assert all("PATH_FRAMING" in str(m[-1].get("content") or "") for m in seen_messages)
    assert seen_messages[0][-1]["content"] != seen_messages[1][-1]["content"]


def test_ibm_sc_paths_do_not_append_unify_path_framing() -> None:
    from apps_rg.runtime.providers.qwen_vllm_provider import ProviderResult
    from apps_rg.runtime.reasoning.bullet_lane_self_consistency import run_qwen_self_consistency_paths

    seen_messages: list[list[dict]] = []

    def _stub(payload: dict, **_: object) -> ProviderResult:
        seen_messages.append(list(payload.get("messages") or []))
        return ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model="m",
            raw_model_output='{"bullets":[]}',
            provider_response={},
        )

    with patch(
        "apps_rg.runtime.reasoning.bullet_lane_self_consistency.call_qwen_vllm",
        side_effect=_stub,
    ):
        run_qwen_self_consistency_paths(
            section_lane="ibm_bullets",
            provider_payload={"model": "m", "messages": [{"role": "user", "content": "base"}]},
            parse_model_json=lambda _r: (None, ""),
            path_count=2,
        )

    assert len(seen_messages) == 2
    assert all("PATH_FRAMING" not in str(m[-1].get("content") or "") for m in seen_messages)
