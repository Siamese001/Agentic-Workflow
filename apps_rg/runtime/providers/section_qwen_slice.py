"""W3 consolidated temporary provider slice — single re-export for section runtimes.

Section dispatches import ``call_qwen_vllm`` from here so direct provider usage is
centralized at one module (carry-forward close-out for f8e3c1).
"""
from __future__ import annotations

from typing import Any

from apps_rg.runtime.providers.qwen_vllm_provider import call_qwen_vllm as _call_qwen_vllm

__all__ = ["call_qwen_vllm"]


def call_qwen_vllm(payload: dict[str, Any]) -> Any:
    """Delegate to apps_rg vLLM client (temporary slice; canonical PA dispatch is future work)."""
    return _call_qwen_vllm(payload)
