"""Shared components for Agentic Workflow.


LOGGER = logging.getLogger(__name__)
Phase 1: Foundation & Reliability - Active Runtime Components
"""
import logging

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant

from .resilience import (
    CircuitBreaker,
    CircuitBreakerState,
    CircuitBreakerOpenError,
    get_breaker,
    ErrorRecoveryManager,
    RecoveryStrategy,
    ResilienceError,
    TransientError,
    PermanentError,
    RetryExhaustedError,
    RateLimiter,
    TokenBucket,
    FixedWindow,
    RateLimitExceeded,
    BackoffStrategy,
    ExponentialBackoff,
    LinearBackoff,
    calculate_backoff_ms,
)

from .reasoning import (
    ReActEngine,
    ReActStep,
    ReActTrace,
    ReasoningMode,
    ReasoningRouter,
    TaskType,
    select_reasoning_strategy,
    ThinkStep,
    ActionStep,
    ObservationStep,
    ReasoningTraceModel,
)

from .mcp import (
    MCPClient,
    MCPClientSpec,
    MCPClientStub,
    MCPClientRegistry,
    MCPError,
    MCPClientInitializationError,
    MCPClientNotFoundError,
    MCPProviderError,
    instantiate_mcp_client,
    parse_mcp_client_specs,
    create_mcp_registry,
    ProviderType,
    get_default_module,
    get_default_class,
)

from .safety import (
    PIIScrubber,
    PIIType,
    PIIMatch,
    PIIResult,
    scrub_pii,
    BiasAuditor,
    BiasType,
    BiasMatch,
    BiasResult,
    audit_bias,
    ConstitutionalAISystem,
    ConstitutionalRule,
    RuleType,
    RuleSeverity,
    ViolationReport,
    ConstitutionalReviewResult,
    review_content,
    ControlPlane,
    SafetyPolicy,
    PolicyDecision,
    PolicyAction,
    create_control_plane,
)

from .caching import (
    SemanticCache,
    CacheEntry,
    CacheHit,
    CacheMiss,
    create_semantic_cache,
    TokenBudget,
    TokenBudgetConfig,
    BudgetExceededError,
    enforce_token_budget,
)


__all__ = [
    # Resilience (Pillar 8)
    "CircuitBreaker",
    "CircuitBreakerState",
    "CircuitBreakerOpenError",
    "get_breaker",
    "ErrorRecoveryManager",
    "RecoveryStrategy",
    "ResilienceError",
    "TransientError",
    "PermanentError",
    "RetryExhaustedError",
    "RateLimiter",
    "TokenBucket",
    "FixedWindow",
    "RateLimitExceeded",
    "BackoffStrategy",
    "ExponentialBackoff",
    "LinearBackoff",
    "calculate_backoff_ms",

    # Reasoning (Pillar 6)
    "ReActEngine",
    "ReActStep",
    "ReActTrace",
    "ReasoningMode",
    "ReasoningRouter",
    "TaskType",
    "select_reasoning_strategy",
    "ThinkStep",
    "ActionStep",
    "ObservationStep",
    "ReasoningTraceModel",

    # MCP (Pillar 3)
    "MCPClient",
    "MCPClientSpec",
    "MCPClientStub",
    "MCPClientRegistry",
    "MCPError",
    "MCPClientInitializationError",
    "MCPClientNotFoundError",
    "MCPProviderError",
    "instantiate_mcp_client",
    "parse_mcp_client_specs",
    "create_mcp_registry",
    "ProviderType",
    "get_default_module",
    "get_default_class",

    # Safety (Pillar 9)
    "PIIScrubber",
    "PIIType",
    "PIIMatch",
    "PIIResult",
    "scrub_pii",
    "BiasAuditor",
    "BiasType",
    "BiasMatch",
    "BiasResult",
    "audit_bias",
    "ConstitutionalAISystem",
    "ConstitutionalRule",
    "RuleType",
    "RuleSeverity",
    "ViolationReport",
    "ConstitutionalReviewResult",
    "review_content",
    "ControlPlane",
    "SafetyPolicy",
    "PolicyDecision",
    "PolicyAction",
    "create_control_plane",

    # Caching (Pillar 11)
    "SemanticCache",
    "CacheEntry",
    "CacheHit",
    "CacheMiss",
    "create_semantic_cache",
    "TokenBudget",
    "TokenBudgetConfig",
    "BudgetExceededError",
    "enforce_token_budget",
]

