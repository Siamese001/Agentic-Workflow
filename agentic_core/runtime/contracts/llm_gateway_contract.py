"""
DS-1: LLM Gateway Contract Extension
Extends SovereignLLMGateway contract with Gemini provider support.
"""

from agentic_core.config.model_catalog import (
    ANTHROPIC_LEGACY_SONNET_35_20241022_MODEL_ID,
    GEMINI_15_FLASH_MODEL_ID,
    OPENAI_GPT4O_MODEL_ID,
    QWEN_LOCAL_MODEL_ID,
)
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Literal
from enum import Enum


class ProviderType(Enum):
    """Supported LLM provider types."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"  # DS-1: Added Gemini support
    QWEN = "qwen"
    AZURE = "azure"


class RoutingStrategy(Enum):
    """Provider routing strategies."""
    SINGLE = "single"
    FALLBACK = "fallback"
    ROUND_ROBIN = "round_robin"
    COST_OPTIMIZED = "cost_optimized"


@dataclass(frozen=True)
class ProviderConfig:
    """Configuration for a single provider."""
    provider: ProviderType
    model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout_seconds: int = 60
    retry_attempts: int = 3
    api_key_env_var: Optional[str] = None  # e.g., "GEMINI_API_KEY"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider.value,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout_seconds": self.timeout_seconds,
            "retry_attempts": self.retry_attempts,
            "api_key_env_var": self.api_key_env_var,
        }


@dataclass(frozen=True)
class LLMGatewayRequest:
    """
    Request to SovereignLLMGateway.
    
    This is the canonical request format that apps_rg (and other apps)
    use to request LLM execution without direct provider contact.
    """
    # Input
    prompt: str
    system_prompt: Optional[str] = None
    
    # Provider selection
    preferred_provider: Optional[ProviderType] = None
    allowed_providers: List[ProviderType] = field(default_factory=list)
    routing_strategy: RoutingStrategy = RoutingStrategy.FALLBACK
    
    # Generation parameters
    temperature: float = 0.7
    max_tokens: int = 4096
    
    # Execution options
    streaming: bool = False
    require_safety_check: bool = True
    
    # Tracing
    request_id: str = ""
    parent_trace_id: Optional[str] = None
    
    def __post_init__(self):
        # Default to all providers if none specified
        if not self.allowed_providers:
            object.__setattr__(
                self, 
                'allowed_providers', 
                list(ProviderType)
            )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_hash": f"sha256:{hash(self.prompt) & 0xFFFFFF:06x}...",  # Privacy: hash only
            "preferred_provider": self.preferred_provider.value if self.preferred_provider else None,
            "allowed_providers": [p.value for p in self.allowed_providers],
            "routing_strategy": self.routing_strategy.value,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "streaming": self.streaming,
            "require_safety_check": self.require_safety_check,
            "request_id": self.request_id,
            "parent_trace_id": self.parent_trace_id,
        }


@dataclass(frozen=True)
class LLMGatewayResponse:
    """
    Response from SovereignLLMGateway.
    
    This is the canonical response format that ensures apps never
    see raw provider responses (controlled egress).
    """
    # Content
    content: str
    content_hash: str  # sha256 for verification
    
    # Provider info
    provider_used: ProviderType
    model_used: str
    
    # Usage
    input_tokens: int
    output_tokens: int
    total_tokens: int
    
    # Performance
    latency_ms: float
    time_to_first_token_ms: Optional[float] = None
    
    # Outcome
    finish_reason: str  # "stop", "length", "content_filter", "error"
    safety_passed: bool
    
    # Error handling
    error_message: Optional[str] = None
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
    
    # Tracing
    gateway_request_id: str = ""
    provider_request_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content_hash": self.content_hash,
            "provider_used": self.provider_used.value,
            "model_used": self.model_used,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "latency_ms": self.latency_ms,
            "time_to_first_token_ms": self.time_to_first_token_ms,
            "finish_reason": self.finish_reason,
            "safety_passed": self.safety_passed,
            "error_message": self.error_message,
            "fallback_used": self.fallback_used,
            "fallback_reason": self.fallback_reason,
            "gateway_request_id": self.gateway_request_id,
            "provider_request_id": self.provider_request_id,
        }


@dataclass(frozen=True)
class LLMGatewayContract:
    """
    DS-1: Full LLM Gateway contract with Gemini support.
    
    This contract defines the interface between apps_rg (ingress-only)
    and the SovereignLLMGateway (core runtime).
    """
    schema_version: str = "1.1.0"  # Bumped for DS-1 Gemini support
    
    # Supported providers
    supported_providers: List[ProviderType] = field(
        default_factory=lambda: [
            ProviderType.ANTHROPIC,
            ProviderType.OPENAI,
            ProviderType.GEMINI,  # DS-1: Gemini now supported
            ProviderType.QWEN,
        ]
    )
    
    # Default routing configuration
    default_routing: Dict[str, Any] = field(default_factory=lambda: {
        "strategy": "fallback",
        "primary": "anthropic",
        "fallbacks": ["gemini", "qwen"],  # DS-1: Gemini in fallback chain
        "criteria": {
            "max_latency_ms": 30000,
            "require_safety": True,
        }
    })
    
    def get_provider_config(self, provider: ProviderType) -> ProviderConfig:
        """Get default config for a provider."""
        configs = {
            ProviderType.ANTHROPIC: ProviderConfig(
                provider=ProviderType.ANTHROPIC,
                model=ANTHROPIC_LEGACY_SONNET_35_20241022_MODEL_ID,
                api_key_env_var="ANTHROPIC_API_KEY",
            ),
            ProviderType.OPENAI: ProviderConfig(
                provider=ProviderType.OPENAI,
                model=OPENAI_GPT4O_MODEL_ID,
                api_key_env_var="OPENAI_API_KEY",
            ),
            ProviderType.GEMINI: ProviderConfig(  # DS-1: Gemini config
                provider=ProviderType.GEMINI,
                model=GEMINI_15_FLASH_MODEL_ID,
                api_key_env_var="GEMINI_API_KEY",
                temperature=0.7,
                max_tokens=4096,
            ),
            ProviderType.QWEN: ProviderConfig(
                provider=ProviderType.QWEN,
                model=QWEN_LOCAL_MODEL_ID,
                api_key_env_var=None,  # Local vLLM, no API key needed
            ),
        }
        return configs.get(provider, configs[ProviderType.ANTHROPIC])
