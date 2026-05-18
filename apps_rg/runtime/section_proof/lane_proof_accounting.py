"""Lane runtime proof placement + generation-status helpers (apps_rg-only).

Centralizes where non-proof runs land under ``runtime_proofs/<lane>/`` and which
provider statuses still permit parsing synthetic/live JSON envelopes.
"""

from __future__ import annotations

from typing import Literal

from apps_rg.runtime.qwen_offline_contract_stub import OFFLINE_CONTRACT_STUB_RUNTIME_STATUS

LanePlacementBucket = Literal["real", "mock", "plumbing"]


def resolve_lane_placement_bucket(
    provider: str,
    *,
    mock_judges: bool,
    offline_stub_env: bool,
) -> LanePlacementBucket:
    """Choose filesystem bucket under ``artifacts/apps_rg/runtime_proofs/<lane>/``.

    - ``mock`` — synthetic generation provider (``--provider mock``).
    - ``plumbing`` — live-ish CLI plumbing that cannot certify product proof
      (mock judges hatch and/or offline Qwen contract stub).
    - ``real`` — default qwen_vllm lane attempts eligible for REAL_LLM rollup pointers.
    """
    p = str(provider or "").strip().lower()
    if p == "mock":
        return "mock"
    if mock_judges or offline_stub_env:
        return "plumbing"
    return "real"


def generation_status_allows_qwen_json_parse(status: str) -> bool:
    """Whether provider JSON parsing/normalization should run like REAL_LLM paths."""
    s = str(status or "").strip()
    return s in ("REAL_LLM", OFFLINE_CONTRACT_STUB_RUNTIME_STATUS)


__all__ = [
    "LanePlacementBucket",
    "OFFLINE_CONTRACT_STUB_RUNTIME_STATUS",
    "generation_status_allows_qwen_json_parse",
    "resolve_lane_placement_bucket",
]
