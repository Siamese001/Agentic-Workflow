from __future__ import annotations

from apps_rg.runtime.sections.prompt_trace_reasoning import (
    attach_reasoning_to_prompt_trace,
)


def test_attach_reasoning_to_prompt_trace_leaves_non_claude_trace_unchanged() -> None:
    trace = {"prompt_id": "headline"}

    out = attach_reasoning_to_prompt_trace(
        trace,
        provider="retired_provider_profile",
        lane_key="headline",
        provider_result_data={"reasoning_execution_receipt": {"id": "r1"}},
    )

    assert out == trace
    assert out is not trace


def test_attach_reasoning_to_prompt_trace_adds_external_claude_receipt() -> None:
    trace = {"prompt_id": "headline"}
    receipt = {"receipt_id": "exec-1", "status": "ok"}

    out = attach_reasoning_to_prompt_trace(
        trace,
        provider="external_claude",
        lane_key="headline",
        provider_result_data={"reasoning_execution_receipt": receipt},
    )

    assert out["reasoning_section_lane"] == "headline"
    assert out["reasoning_execution_receipt"] == receipt
    assert "reasoning_section_lane" not in trace


def test_attach_reasoning_to_prompt_trace_handles_missing_provider_data() -> None:
    out = attach_reasoning_to_prompt_trace(
        {"prompt_id": "headline"},
        provider="external_claude",
        lane_key="headline",
        provider_result_data=None,
    )

    assert out == {
        "prompt_id": "headline",
        "reasoning_section_lane": "headline",
    }
