"""Agentic Core Mixins.

This module provides shared capability mixins for agent composition.
Mixins are organized by functional area and are used by base agents and layer-specific implementations.

Core Infrastructure Mixins (used by SovereignBaseAgent):
- ADGBehavioralMixin: ADG behavioral tracking
- AtomicExecutionMixin: Atomic execution guarantees
- AuditTrailMixin: Audit trail tracking
- ConfigMixin: Configuration management (direct import only - circular import risk)
- EmbeddingMixin: Embedding operations
- GoldenContextMixin: Golden context management
- InfrastructureMixin: Infrastructure consolidation (direct import only - circular import risk)
- LLMProviderMixin: LLM provider abstraction
- MetaLearningClientMixin: Meta-learning client
- RuntimeSafetyMixin: Runtime safety checks
- ValidatorMixin: Validation capabilities

Runtime/Utility Mixins:
- MetricsMixin, MetricsProtocol: Metrics collection
- SafetyAnalysisMixin: Safety analysis
- CacheConfig, CacheEntry: Caching utilities
- SpanContext, TracingMixin: Distributed tracing
- HealingPolicyMixin: Healing capabilities

Layer-Specific Mixins:
- PromptRenderingMixin: Prompt rendering (L5_safety)
- SurgicalCSTHealerMixin: CST healing (L5_safety)
- HallucinationDetectionMixin: Hallucination detection (L5_safety)
- InspectionCapability: Inspection capabilities (L5_safety)
- HealerAgentMixin: Healing agent (L3_orchestration)
- RedisCacheMixin: Redis caching (L2_execution)
- SemanticCacheMixin: Semantic caching (apps)

Note: Many mixins have circular import dependencies when loaded via __init__.py.
Import mixins directly from their modules when needed.
"""

# Only export mixins that don't trigger circular imports
from .adg_behavioral_mixin import ADGBehavioralMixin
from .atomic_execution_mixin import AtomicExecutionMixin
from .audit_trail_mixin import AuditTrailMixin
from .metrics_mixin import MetricsMixin, MetricsProtocol

__all__ = [
    "ADGBehavioralMixin",
    "AtomicExecutionMixin",
    "AuditTrailMixin",
    "MetricsMixin",
    "MetricsProtocol",
]
