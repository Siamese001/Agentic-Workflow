"""Qwen offline contract stub — **disabled** for apps_rg product runs.

Historical tests used ``APPS_RG_QWEN_OFFLINE_CONTRACT_STUB=1``; runtime now requires live
``qwen_vllm`` only. See ``qwen_live_only_guard.assert_live_qwen_vllm_no_mocks``.
"""
from __future__ import annotations

import os

from apps_rg.runtime.providers.qwen_vllm_provider import ProviderResult

ENV_APPS_RG_QWEN_OFFLINE_CONTRACT_STUB = "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB"
ENV_APPS_RG_QWEN_DISABLE_OFFLINE_STUB = "APPS_RG_QWEN_DISABLE_OFFLINE_STUB"

OFFLINE_CONTRACT_STUB_RUNTIME_STATUS = "OFFLINE_CONTRACT_STUB"

_STUB_DISABLED_MSG = (
    "Qwen offline contract stub is disabled. Unset APPS_RG_QWEN_OFFLINE_CONTRACT_STUB "
    "and run with live qwen_vllm (vLLM reachable at VLLM_BASE_URL)."
)


def offline_contract_stub_enabled() -> bool:
    return False


def effective_offline_contract_stub_enabled() -> bool:
    return False


def synthetic_qwen_provider_result(*, raw_model_output: str, requested_model: str) -> ProviderResult:
    raise RuntimeError(_STUB_DISABLED_MSG)


__all__ = [
    "ENV_APPS_RG_QWEN_DISABLE_OFFLINE_STUB",
    "ENV_APPS_RG_QWEN_OFFLINE_CONTRACT_STUB",
    "OFFLINE_CONTRACT_STUB_RUNTIME_STATUS",
    "effective_offline_contract_stub_enabled",
    "offline_contract_stub_enabled",
    "synthetic_qwen_provider_result",
]
