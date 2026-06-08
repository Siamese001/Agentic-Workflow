"""Provider-neutral result/request contracts for apps_rg model providers.

These dataclasses are the canonical shape returned by **every** apps_rg provider
(external Claude, external OpenAI, and historically the local Qwen slice). They are
deliberately provider-agnostic and carry no transport logic so the selection surface
(`provider_gateway`, `section_provider_call`) and the section lanes can depend on a
stable contract without importing any concrete provider implementation.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from apps_rg.runtime.artifact_secret_redaction import redact_sensitive_mapping


@dataclass
class ProviderRequest:
    provider_requested: str
    provider_attempted: bool
    provider_url: str
    model: str
    temperature: float
    max_tokens: int
    timeout_seconds: int
    prompt_hash: str
    input_payload_hash: str
    mock_fallback_allowed: bool

    def to_dict(self) -> dict[str, Any]:
        return redact_sensitive_mapping(asdict(self))


@dataclass
class ProviderResult:
    provider_requested: str
    provider_attempted: bool
    provider_available: bool
    exact_provider_error: str | None
    runtime_generation_status: str  # REAL_LLM | BLOCKED | MOCKED | STUBBED
    model: str
    raw_model_output: str
    provider_response: dict[str, Any] | None
    reasoning_execution_receipt: dict[str, Any] | None = None
    stub: bool = False
    apps_rg_qwen_preflight_blocked: bool = False
    apps_rg_last_probe_snapshot: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


__all__ = ["ProviderRequest", "ProviderResult"]
