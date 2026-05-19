"""prompt_selection_trace.json helpers — reasoning lane + receipt snapshot.

W11-M4A: canonical home under ``apps_rg.runtime.sections`` (lanes SSOT).
``apps_rg.runtime.dispatch.prompt_trace_reasoning`` re-exports for compatibility.
"""

from __future__ import annotations

from typing import Any


def attach_reasoning_to_prompt_trace(
    trace: dict[str, Any],
    *,
    provider: str,
    lane_key: str,
    provider_result_data: dict[str, Any] | None,
) -> dict[str, Any]:
    """When using qwen_vllm, expose exec-trace-aligned keys for downstream X1 merges."""
    out = dict(trace)
    if provider != "qwen_vllm":
        return out
    out["reasoning_section_lane"] = lane_key
    rec = None
    if isinstance(provider_result_data, dict):
        rec = provider_result_data.get("reasoning_execution_receipt")
    if rec is not None:
        out["reasoning_execution_receipt"] = rec
    return out
