"""Deterministic Qwen-shaped response for contract tests (no live vLLM).

Set ``APPS_RG_QWEN_OFFLINE_CONTRACT_STUB=1`` so section lanes write OpenAI-shaped
``provider_response.json`` without HTTP, recording ``runtime_generation_status=OFFLINE_CONTRACT_STUB``.
This is **not** a separate generation provider: ``--provider`` remains ``qwen_vllm`` only.
"""
from __future__ import annotations

import os
from typing import Any

from apps_rg.runtime.providers.qwen_vllm_provider import ProviderResult

ENV_APPS_RG_QWEN_OFFLINE_CONTRACT_STUB = "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB"
# Test / live-transport hook: when set, dispatch uses real `call_qwen_vllm` even if
# ``APPS_RG_QWEN_OFFLINE_CONTRACT_STUB=1`` (monkeypatched HTTP still exercises transport).
ENV_APPS_RG_QWEN_DISABLE_OFFLINE_STUB = "APPS_RG_QWEN_DISABLE_OFFLINE_STUB"

# Distinct from REAL_LLM transport proof — recorded when synthetic Qwen-shaped output is emitted.
OFFLINE_CONTRACT_STUB_RUNTIME_STATUS = "OFFLINE_CONTRACT_STUB"

_TRUE = frozenset({"1", "true", "yes", "on", "y"})


def offline_contract_stub_enabled() -> bool:
    raw = os.environ.get(ENV_APPS_RG_QWEN_OFFLINE_CONTRACT_STUB, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def effective_offline_contract_stub_enabled() -> bool:
    """True when offline contract stub applies to early synthetic dispatch paths."""
    if str(os.environ.get(ENV_APPS_RG_QWEN_DISABLE_OFFLINE_STUB, "") or "").strip().lower() in _TRUE:
        return False
    return offline_contract_stub_enabled()


def synthetic_qwen_provider_result(*, raw_model_output: str, requested_model: str) -> ProviderResult:
    response_data: dict[str, Any] = {
        "model": requested_model,
        "choices": [{"message": {"content": raw_model_output}}],
        "stub": True,
        "offline_contract_stub_reason": ENV_APPS_RG_QWEN_OFFLINE_CONTRACT_STUB,
    }
    return ProviderResult(
        provider_requested="qwen_vllm",
        provider_attempted=True,
        provider_available=True,
        exact_provider_error=None,
        runtime_generation_status=OFFLINE_CONTRACT_STUB_RUNTIME_STATUS,
        model=str(requested_model).strip(),
        raw_model_output=raw_model_output,
        provider_response=response_data,
        stub=True,
    )


__all__ = [
    "ENV_APPS_RG_QWEN_DISABLE_OFFLINE_STUB",
    "ENV_APPS_RG_QWEN_OFFLINE_CONTRACT_STUB",
    "OFFLINE_CONTRACT_STUB_RUNTIME_STATUS",
    "effective_offline_contract_stub_enabled",
    "offline_contract_stub_enabled",
    "synthetic_qwen_provider_result",
]
