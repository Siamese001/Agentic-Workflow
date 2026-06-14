"""Provider types for generic provider gateway.

RB13: apps-rg-zip-based-full-spine-runtime-restoration-v1

Generic, app-agnostic provider invocation contracts.
No app-specific code. No hardcoded provider names.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class ProviderKind(str, Enum):
    """Provider implementation kinds."""
    
    STUB = "stub"
    LOCAL_VLLM = "local_vllm"
    EXTERNAL_API = "external_api"
    DETERMINISTIC = "deterministic"


class ProviderMode(str, Enum):
    """Provider mode from activation profile."""
    
    STUB_ONLY = "stub_only"
    LOCAL_ONLY = "local_only"
    LIVE_ALLOWED = "live_allowed"


class BudgetStatus(str, Enum):
    """Budget enforcement status."""
    
    WITHIN_BUDGET = "within_budget"
    BUDGET_EXCEEDED = "budget_exceeded"
    BUDGET_UNKNOWN = "budget_unknown"


class TimeoutStatus(str, Enum):
    """Timeout enforcement status."""
    
    WITHIN_LIMIT = "within_limit"
    TIMEOUT_EXCEEDED = "timeout_exceeded"
    TIMEOUT_UNKNOWN = "timeout_unknown"


class SafetyStatus(str, Enum):
    """Safety/content filter status."""
    
    SAFE = "safe"
    FLAGGED = "flagged"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ProviderProfile:
    """Loaded provider profile from app config.
    
    All external secrets referenced by env var name only.
    """
    
    profile_id: str
    provider_kind: ProviderKind
    model_id: Optional[str] = None
    endpoint_url: Optional[str] = None
    endpoint_env_var: Optional[str] = None
    api_key_env_var: Optional[str] = None
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    max_tokens: int = 4096
    timeout_seconds: int = 60
    temperature_range: tuple[float, float] = (0.0, 1.0)
    requires_network: bool = False
    sandbox_safe: bool = True
    activation_env_var: Optional[str] = None
    vendor: str = ""


@dataclass(frozen=True)
class TokenUsage:
    """Token consumption from a provider invocation."""
    
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    def as_dict(self) -> Dict[str, int]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass(frozen=True)
class ProviderInvocationReceipt:
    """Receipt for every provider invocation.
    
    Required fields per RB13 specification.
    """
    
    invocation_id: str
    provider_profile_ref: str
    provider_kind: ProviderKind
    model_ref: Optional[str]
    request_id: str
    run_id: str
    trace_root: str
    node_id: str
    prompt_artifact_ref: str
    input_digest: str
    output_digest: str
    latency_ms: float
    token_usage: TokenUsage
    budget_status: BudgetStatus
    timeout_status: TimeoutStatus
    safety_status: SafetyStatus
    error: Optional[str] = None
    deterministic_digest: str = ""
    
    def as_dict(self) -> Dict[str, Any]:
        return {
            "invocation_id": self.invocation_id,
            "provider_profile_ref": self.provider_profile_ref,
            "provider_kind": self.provider_kind.value,
            "model_ref": self.model_ref,
            "request_id": self.request_id,
            "run_id": self.run_id,
            "trace_root": self.trace_root,
            "node_id": self.node_id,
            "prompt_artifact_ref": self.prompt_artifact_ref,
            "input_digest": self.input_digest,
            "output_digest": self.output_digest,
            "latency_ms": round(self.latency_ms, 2),
            "token_usage": self.token_usage.as_dict(),
            "budget_status": self.budget_status.value,
            "timeout_status": self.timeout_status.value,
            "safety_status": self.safety_status.value,
            "error": self.error,
            "deterministic_digest": self.deterministic_digest,
            "schema_version": "rb13.1",
        }


@dataclass(frozen=True)
class ProviderRequest:
    """Request to invoke a provider."""
    
    prompt_text: str
    provider_profile: ProviderProfile
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    # OpenAI-compatible chat.completions only; omit when None (server default).
    openai_response_format: Optional[Dict[str, Any]] = None
    request_id: str = ""
    run_id: str = ""
    trace_root: str = ""
    node_id: str = ""
    prompt_artifact_ref: str = ""
    # --- Anthropic provider-native fields (additive; only consulted when vendor == "anthropic") ---
    # When set, the gateway sends this structured Messages-API payload (system / messages /
    # tools / tool_choice / metadata / cache_control markers / thinking / citations / etc.)
    # verbatim instead of flattening ``prompt_text`` into a single user message. It MUST NOT
    # contain ``model`` / ``max_tokens`` / ``temperature`` — the gateway owns those (rejected
    # fail-closed). ``prompt_text`` remains the legacy/back-compat path when this is None.
    anthropic_payload: Optional[Dict[str, Any]] = None
    # Beta features requiring an ``anthropic-beta`` header (e.g.
    # ("mid-conversation-system-2026-04-07",)). No beta is enabled by default; the gateway
    # only sends the header when this tuple is non-empty.
    anthropic_beta_headers: tuple[str, ...] = ()
    # Additional per-request headers, merged after beta headers. A conflicting ``anthropic-beta``
    # key here when ``anthropic_beta_headers`` is also set fails closed.
    anthropic_extra_headers: Optional[Dict[str, str]] = None
    # Advisory streaming hint (reserved; the gateway does not yet stream).
    stream: bool = False


@dataclass(frozen=True)
class ProviderResponse:
    """Response from a provider invocation."""
    
    success: bool
    text: str
    receipt: ProviderInvocationReceipt
    error_message: Optional[str] = None
    model_used: Optional[str] = None
    invocation_meta: Optional[Dict[str, Any]] = None


class ProviderGatewayError(Exception):
    """Base exception for provider gateway failures."""
    pass


class ProviderProfileNotFoundError(ProviderGatewayError):
    """Raised when requested provider profile not found."""
    pass


class ProviderNotAllowedError(ProviderGatewayError):
    """Raised when provider not in step contract allowlist."""
    pass


class ProviderCredentialsMissingError(ProviderGatewayError):
    """Raised when external provider credentials not available."""
    pass


class ProviderModeBlockedError(ProviderGatewayError):
    """Raised when live provider blocked by activation profile."""
    pass


__all__ = [
    "ProviderKind",
    "ProviderMode", 
    "BudgetStatus",
    "TimeoutStatus",
    "SafetyStatus",
    "ProviderProfile",
    "TokenUsage",
    "ProviderInvocationReceipt",
    "ProviderRequest",
    "ProviderResponse",
    "ProviderGatewayError",
    "ProviderProfileNotFoundError",
    "ProviderNotAllowedError",
    "ProviderCredentialsMissingError",
    "ProviderModeBlockedError",
]
