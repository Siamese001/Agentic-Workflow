"""CLI preflight shims for ``python -m apps_rg --section <lane>`` (apps_rg only).

The local Qwen/vLLM Docker + HTTP ``/v1/models`` reachability gate was removed with the
local-model provider. The external generation provider owns its own transport and reports a
BLOCKED ``ProviderResult`` on failure, so section-CLI runs no longer require a local-container
health preflight. These functions remain as no-ops for the dispatch chain.
"""
from __future__ import annotations

import os
from typing import Any

_ENV_SKIP_QWEN_HEALTH = "APPS_RG_SKIP_QWEN_VLLM_HEALTH"


def _truthy_env(name: str) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return False
    return str(raw).strip().lower() in {"1", "true", "yes", "y", "on"}


def should_skip_qwen_vllm_health_gate() -> bool:
    """No local-provider health gate exists; always skip (kept for dispatch-chain compatibility)."""
    return True


def require_qwen_vllm_cli_health(
    *,
    lane_provider: str,
    docker_restart_audit: dict[str, Any] | None = None,
) -> None:
    """No-op: the external provider needs no local-container health gate."""
    return None


__all__ = [
    "require_qwen_vllm_cli_health",
    "should_skip_qwen_vllm_health_gate",
]
