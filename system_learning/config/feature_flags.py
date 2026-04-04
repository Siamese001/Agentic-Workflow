"""Feature flags for system learning signal enhancement phases.

Controls the rollout of new functionality across all phases.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FeatureFlagConfig:
    """Configuration for feature flags."""

    # Phase 1A: ADG Foundation
    enable_adg_rca_integration: bool = True
    enable_adg_hotspots: bool = True
    enable_adg_drift_detection: bool = True

    # Phase 1B: Safety & Governance
    enable_circuit_breaker_tracking: bool = True
    enable_template_drift_detection: bool = True
    enable_adg_confidence_tiers: bool = True
    enable_safety_audit_emission: bool = True

    # Phase 2: Execution & Orchestration
    enable_injection_monitoring: bool = True
    enable_healing_tier_tracking: bool = True
    enable_workflow_outcome_intake: bool = True
    enable_tier_dispatch_optimization: bool = True
    enable_execution_trace_enhancement: bool = True
    enable_orchestration_signal_emission: bool = True

    # Phase 3: Resource & Memory Integration
    enable_resource_prediction_tracking: bool = True
    enable_healing_memory_quality: bool = True
    enable_phase_outcome_intake: bool = True
    enable_repair_route_serialization: bool = True

    # Phase 4: Cross-Domain & Infrastructure
    enable_cache_coherence_violations: bool = True
    enable_infrastructure_drift_detection: bool = True
    enable_cross_domain_healing_events: bool = True
    enable_cross_domain_pattern_analysis: bool = True

    # Phase 5: Advanced Integration
    enable_otel_span_collection: bool = True
    enable_otel_telemetry_store: bool = True
    enable_injection_context_tracking: bool = True
    enable_signal_spike_detection: bool = True

    # Phase 6: Final Integration
    enable_end_to_end_validation: bool = True
    enable_performance_monitoring: bool = True
    enable_graceful_degradation: bool = True

    @classmethod
    def from_env(cls) -> FeatureFlagConfig:
        """Create configuration from environment variables.

        Returns:
            FeatureFlagConfig instance with env overrides
        """
        # Default configuration
        config = cls()

        # Environment variable overrides
        env_overrides = {
            "SL_ENABLE_ADG_RCA_INTEGRATION": "enable_adg_rca_integration",
            "SL_ENABLE_ADG_HOTSPOTS": "enable_adg_hotspots",
            "SL_ENABLE_ADG_DRIFT_DETECTION": "enable_adg_drift_detection",
            "SL_ENABLE_CIRCUIT_BREAKER_TRACKING": "enable_circuit_breaker_tracking",
            "SL_ENABLE_TEMPLATE_DRIFT_DETECTION": "enable_template_drift_detection",
            "SL_ENABLE_ADG_CONFIDENCE_TIERS": "enable_adg_confidence_tiers",
            "SL_ENABLE_SAFETY_AUDIT_EMISSION": "enable_safety_audit_emission",
            "SL_ENABLE_INJECTION_MONITORING": "enable_injection_monitoring",
            "SL_ENABLE_HEALING_TIER_TRACKING": "enable_healing_tier_tracking",
            "SL_ENABLE_WORKFLOW_OUTCOME_INTAKE": "enable_workflow_outcome_intake",
            "SL_ENABLE_TIER_DISPATCH_OPTIMIZATION": "enable_tier_dispatch_optimization",
            "SL_ENABLE_EXECUTION_TRACE_ENHANCEMENT": "enable_execution_trace_enhancement",
            "SL_ENABLE_ORCHESTRATION_SIGNAL_EMISSION": "enable_orchestration_signal_emission",
            "SL_ENABLE_RESOURCE_PREDICTION_TRACKING": "enable_resource_prediction_tracking",
            "SL_ENABLE_HEALING_MEMORY_QUALITY": "enable_healing_memory_quality",
            "SL_ENABLE_PHASE_OUTCOME_INTAKE": "enable_phase_outcome_intake",
            "SL_ENABLE_REPAIR_ROUTE_SERIALIZATION": "enable_repair_route_serialization",
            "SL_ENABLE_CACHE_COHERENCE_VIOLATIONS": "enable_cache_coherence_violations",
            "SL_ENABLE_INFRASTRUCTURE_DRIFT_DETECTION": "enable_infrastructure_drift_detection",
            "SL_ENABLE_CROSS_DOMAIN_HEALING_EVENTS": "enable_cross_domain_healing_events",
            "SL_ENABLE_CROSS_DOMAIN_PATTERN_ANALYSIS": "enable_cross_domain_pattern_analysis",
            "SL_ENABLE_OTEL_SPAN_COLLECTION": "enable_otel_span_collection",
            "SL_ENABLE_OTEL_TELEMETRY_STORE": "enable_otel_telemetry_store",
            "SL_ENABLE_INJECTION_CONTEXT_TRACKING": "enable_injection_context_tracking",
            "SL_ENABLE_SIGNAL_SPIKE_DETECTION": "enable_signal_spike_detection",
            "SL_ENABLE_END_TO_END_VALIDATION": "enable_end_to_end_validation",
            "SL_ENABLE_PERFORMANCE_MONITORING": "enable_performance_monitoring",
            "SL_ENABLE_GRACEFUL_DEGRADATION": "enable_graceful_degradation",
        }

        # Apply environment overrides
        config_dict = {}
        for env_var, attr_name in env_overrides.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                config_dict[attr_name] = env_value.lower() in ("true", "1", "yes", "on")

        return config(**config_dict) if config_dict else config

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of feature flags
        """
        return {
            "phase_1a": {
                "adg_rca_integration": self.enable_adg_rca_integration,
                "adg_hotspots": self.enable_adg_hotspots,
                "adg_drift_detection": self.enable_adg_drift_detection,
            },
            "phase_1b": {
                "circuit_breaker_tracking": self.enable_circuit_breaker_tracking,
                "template_drift_detection": self.enable_template_drift_detection,
                "adg_confidence_tiers": self.enable_adg_confidence_tiers,
                "safety_audit_emission": self.enable_safety_audit_emission,
            },
            "phase_2": {
                "injection_monitoring": self.enable_injection_monitoring,
                "healing_tier_tracking": self.enable_healing_tier_tracking,
                "workflow_outcome_intake": self.enable_workflow_outcome_intake,
                "tier_dispatch_optimization": self.enable_tier_dispatch_optimization,
                "execution_trace_enhancement": self.enable_execution_trace_enhancement,
                "orchestration_signal_emission": self.enable_orchestration_signal_emission,
            },
            "phase_3": {
                "resource_prediction_tracking": self.enable_resource_prediction_tracking,
                "healing_memory_quality": self.enable_healing_memory_quality,
                "phase_outcome_intake": self.enable_phase_outcome_intake,
                "repair_route_serialization": self.enable_repair_route_serialization,
            },
            "phase_4": {
                "cache_coherence_violations": self.enable_cache_coherence_violations,
                "infrastructure_drift_detection": self.enable_infrastructure_drift_detection,
                "cross_domain_healing_events": self.enable_cross_domain_healing_events,
                "cross_domain_pattern_analysis": self.enable_cross_domain_pattern_analysis,
            },
            "phase_5": {
                "otel_span_collection": self.enable_otel_span_collection,
                "otel_telemetry_store": self.enable_otel_telemetry_store,
                "injection_context_tracking": self.enable_injection_context_tracking,
                "signal_spike_detection": self.enable_signal_spike_detection,
            },
            "phase_6": {
                "end_to_end_validation": self.enable_end_to_end_validation,
                "performance_monitoring": self.enable_performance_monitoring,
                "graceful_degradation": self.enable_graceful_degradation,
            },
        }


# Global feature flag configuration
_feature_config: FeatureFlagConfig | None = None


def get_feature_flags() -> FeatureFlagConfig:
    """Get the global feature flag configuration.

    Returns:
        FeatureFlagConfig instance
    """
    global _feature_config
    if _feature_config is None:
        _feature_config = FeatureFlagConfig.from_env()
    return _feature_config


def is_feature_enabled(feature_name: str) -> bool:
    """Check if a specific feature is enabled.

    Args:
        feature_name: Name of the feature to check

    Returns:
        True if feature is enabled
    """
    flags = get_feature_flags()
    return getattr(flags, feature_name, False)


def reset_feature_flags() -> None:
    """Reset feature flags configuration (for testing)."""
    global _feature_config
    _feature_config = None
