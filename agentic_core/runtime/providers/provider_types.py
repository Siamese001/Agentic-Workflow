"""Provider types for generic provider gateway.

RB13: apps-rg-zip-based-full-spine-runtime-restoration-v1

Generic, app-agnostic provider invocation contracts.
No app-specific code. No hardcoded provider names.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


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


class ModelCapability(str, Enum):
    """Provider-neutral model capabilities used for routing decisions."""

    TEXT_GENERATION = "text_generation"
    STRUCTURED_OUTPUT = "structured_output"
    TOOL_CALLING = "tool_calling"
    STREAMING = "streaming"
    LOCAL_INFERENCE = "local_inference"
    EMBEDDINGS = "embeddings"
    VISION_INPUT = "vision_input"


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
class ProviderCapabilityProfile:
    """Provider-neutral capability metadata for model routing.

    This is intentionally separate from vendor payload fields. Runtime packages
    can select profiles by required capabilities, while provider adapters keep
    the vendor-specific request translation behind the gateway.
    """

    capabilities: tuple[ModelCapability | str, ...] = field(default_factory=tuple)
    max_context_tokens: int | None = None
    max_output_tokens: int | None = None
    supports_json_schema: bool = False
    supports_tool_choice: bool = False
    supports_batch: bool = False
    latency_class: str = "unknown"

    def supports(self, capability: ModelCapability | str) -> bool:
        target = capability.value if isinstance(capability, ModelCapability) else str(capability)
        return target in {
            item.value if isinstance(item, ModelCapability) else str(item)
            for item in self.capabilities
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "capabilities": [
                item.value if isinstance(item, ModelCapability) else str(item)
                for item in self.capabilities
            ],
            "max_context_tokens": self.max_context_tokens,
            "max_output_tokens": self.max_output_tokens,
            "supports_json_schema": self.supports_json_schema,
            "supports_tool_choice": self.supports_tool_choice,
            "supports_batch": self.supports_batch,
            "latency_class": self.latency_class,
        }


@dataclass(frozen=True)
class ProviderOutputContract:
    """Provider-neutral response contract requested by a caller."""

    response_mime_type: str = "text/plain"
    json_schema: dict[str, Any] | None = None
    required_capabilities: tuple[ModelCapability | str, ...] = field(default_factory=tuple)

    def requires(self, capability: ModelCapability | str) -> bool:
        target = capability.value if isinstance(capability, ModelCapability) else str(capability)
        return target in {
            item.value if isinstance(item, ModelCapability) else str(item)
            for item in self.required_capabilities
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "response_mime_type": self.response_mime_type,
            "json_schema": self.json_schema,
            "required_capabilities": [
                item.value if isinstance(item, ModelCapability) else str(item)
                for item in self.required_capabilities
            ],
        }


@dataclass(frozen=True)
class ProviderProfile:
    """Loaded provider profile from app config.

    All external secrets referenced by env var name only.
    """

    profile_id: str
    provider_kind: ProviderKind
    model_id: str | None = None
    endpoint_url: str | None = None
    endpoint_env_var: str | None = None
    api_key_env_var: str | None = None
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    capability_profile: ProviderCapabilityProfile = field(default_factory=ProviderCapabilityProfile)
    max_tokens: int = 4096
    timeout_seconds: int = 60
    temperature_range: tuple[float, float] = (0.0, 1.0)
    requires_network: bool = False
    sandbox_safe: bool = True
    activation_env_var: str | None = None
    vendor: str = ""


@dataclass(frozen=True)
class TokenUsage:
    """Token consumption from a provider invocation."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def as_dict(self) -> dict[str, int]:
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
    model_ref: str | None
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
    error: str | None = None
    deterministic_digest: str = ""

    def as_dict(self) -> dict[str, Any]:
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
    max_tokens: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    output_contract: ProviderOutputContract = field(default_factory=ProviderOutputContract)
    # OpenAI-compatible chat.completions only; omit when None (server default).
    openai_response_format: dict[str, Any] | None = None
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
    anthropic_payload: dict[str, Any] | None = None
    # Beta features requiring an ``anthropic-beta`` header (e.g.
    # ("mid-conversation-system-2026-04-07",)). No beta is enabled by default; the gateway
    # only sends the header when this tuple is non-empty.
    anthropic_beta_headers: tuple[str, ...] = ()
    # Additional per-request headers, merged after beta headers. A conflicting ``anthropic-beta``
    # key here when ``anthropic_beta_headers`` is also set fails closed.
    anthropic_extra_headers: dict[str, str] | None = None
    # Advisory streaming hint (reserved; the gateway does not yet stream).
    stream: bool = False


@dataclass(frozen=True)
class ProviderResponse:
    """Response from a provider invocation."""

    success: bool
    text: str
    receipt: ProviderInvocationReceipt
    error_message: str | None = None
    model_used: str | None = None
    invocation_meta: dict[str, Any] | None = None


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
    "ModelCapability",
    "BudgetStatus",
    "TimeoutStatus",
    "SafetyStatus",
    "ProviderCapabilityProfile",
    "ProviderOutputContract",
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
