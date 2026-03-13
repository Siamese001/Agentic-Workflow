"""
SSOT Mixin Stack — Canonical MRO-Safe Composite Mixin.

Bundles all SSOT mixins in the correct MRO order for integration
into execute_ssot.py decision engines.

MRO Order (left-to-right, most-specific first):
  1. SSOTFeatureFlagMixin      — L4-sourced flags (read-only)
  2. SSOTMetaLearningMixin     — Gated advisory pattern storage
  3. SSOTHallucinationDetectionMixin — Advisory hallucination detection
  4. SSOTCognitiveRecoveryMixin — Advisory recovery hints
  5. SSOTSelfDiagnosisMixin    — L4 aggregate health reader
  6. SSOTAdaptiveExecutionMixin — L4-derived mode selection
  7. SSOTContextPropagationMixin — ContextVar propagation
  8. SSOTTracingMixin           — Span management
  9. SSOTStateValidationMixin   — Pre/post-condition guards
  10. SSOTRateLimitMixin        — Rate limiting
  11. SSOTCircuitBreakerMixin   — Circuit breaker
  12. SSOTCachingMixin          — In-memory cache
  13. SSOTMetricsMixin          — Observability metrics
  14. SSOTAuditTrailMixin       — Cryptographic audit chain
  15. ReplayGuardMixin          — Foundation (must be last SSOT mixin)

Usage:
    class SovereignDecisionEngine(SSOTMixinStack, AutonomousDecisionEngine):
        pass
"""

from __future__ import annotations

from agentic_core.mixins.replay_guard_mixin import ReplayGuardMixin
from agentic_core.mixins.ssot_adaptive_execution_mixin import SSOTAdaptiveExecutionMixin
from agentic_core.mixins.ssot_audit_trail_mixin import SSOTAuditTrailMixin
from agentic_core.mixins.ssot_caching_mixin import SSOTCachingMixin
from agentic_core.mixins.ssot_circuit_breaker_mixin import SSOTCircuitBreakerMixin
from agentic_core.mixins.ssot_cognitive_recovery_mixin import SSOTCognitiveRecoveryMixin
from agentic_core.mixins.ssot_context_propagation_mixin import SSOTContextPropagationMixin
from agentic_core.mixins.ssot_feature_flag_mixin import SSOTFeatureFlagMixin
from agentic_core.mixins.ssot_hallucination_detection_mixin import SSOTHallucinationDetectionMixin
from agentic_core.mixins.ssot_meta_learning_mixin import SSOTMetaLearningMixin
from agentic_core.mixins.ssot_metrics_mixin import SSOTMetricsMixin
from agentic_core.mixins.ssot_rate_limit_mixin import SSOTRateLimitMixin
from agentic_core.mixins.ssot_self_diagnosis_mixin import SSOTSelfDiagnosisMixin
from agentic_core.mixins.ssot_state_validation_mixin import SSOTStateValidationMixin
from agentic_core.mixins.ssot_tracing_mixin import SSOTTracingMixin


class SSOTMixinStack(
    SSOTFeatureFlagMixin,
    SSOTMetaLearningMixin,
    SSOTHallucinationDetectionMixin,
    SSOTCognitiveRecoveryMixin,
    SSOTSelfDiagnosisMixin,
    SSOTAdaptiveExecutionMixin,
    SSOTContextPropagationMixin,
    SSOTTracingMixin,
    SSOTStateValidationMixin,
    SSOTRateLimitMixin,
    SSOTCircuitBreakerMixin,
    SSOTCachingMixin,
    SSOTMetricsMixin,
    SSOTAuditTrailMixin,
    ReplayGuardMixin,
):
    """Canonical composite mixin bundling all SSOT mixins.

    This class exists solely to provide a single MRO-safe entry point
    for integrating the full SSOT mixin stack into decision engines.
    All mixins use cooperative ``super().__init__(**kwargs)`` chaining.
    """

    pass


__all__ = ["SSOTMixinStack"]
