"""
LIC Outreach Pipeline Configuration

Defines LIC defaults for reasoning profile preset, retrieval depth,
KG usage flags, safety profile selection, and concurrency/batching settings.
ZERO business logic. Pure config dataclasses + constants.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

from config.LIC.lic_profile import LICHyperparameters, LICSafetyStrictness, LICConcurrencyMode


class LICReasoningPreset(str, Enum):
    """Reasoning intensity presets for LIC operations."""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    RESEARCH = "research"


class LICRetrievalMode(str, Enum):
    """Retrieval modes for LIC operations."""
    FAST = "fast"
    COMPREHENSIVE = "comprehensive"
    DEEP = "deep"


@dataclass
class LICSafetyProfile:
    """Safety profile configuration for LIC."""
    strictness: LICSafetyStrictness
    enable_pii_detection: bool
    enable_bias_auditing: bool
    enable_content_filtering: bool
    blocked_content_types: List[str]
    required_approvals: List[str]


@dataclass
class LICConcurrencyConfig:
    """Concurrency and batching configuration."""
    mode: LICConcurrencyMode
    max_parallel_tasks: int
    batch_size: int
    timeout_seconds: int
    retry_attempts: int


@dataclass
class LICPipelineConfig:
    """Complete LIC pipeline configuration."""
    
    # Core Configuration
    reasoning_preset: LICReasoningPreset
    retrieval_mode: LICRetrievalMode
    hyperparameters: LICHyperparameters
    
    # Safety Configuration
    safety_profile: LICSafetyProfile
    
    # Concurrency Configuration
    concurrency: LICConcurrencyConfig
    
    # Feature Flags
    enable_company_research: bool = True
    enable_contact_research: bool = True
    enable_message_generation: bool = True
    enable_rag_enrichment: bool = True
    enable_kg_fallback: bool = True
    enable_temporal_search: bool = True
    
    # Performance Configuration
    cost_limit_per_run: float = 10.0
    latency_limit_seconds: float = 30.0
    enable_telemetry: bool = False
    
    # Quality Configuration
    min_confidence_threshold: float = 0.7
    max_results_per_query: int = 10
    enable_result_deduplication: bool = True


# Default LIC Pipeline Configurations
DEFAULT_LIC_CONFIG = LICPipelineConfig(
    reasoning_preset=LICReasoningPreset.BALANCED,
    retrieval_mode=LICRetrievalMode.COMPREHENSIVE,
    hyperparameters=LICHyperparameters(),
    safety_profile=LICSafetyProfile(
        strictness=LICSafetyStrictness.STANDARD,
        enable_pii_detection=True,
        enable_bias_auditing=True,
        enable_content_filtering=True,
        blocked_content_types=["spam", "harassment", "illegal_content"],
        required_approvals=[]
    ),
    concurrency=LICConcurrencyConfig(
        mode=LICConcurrencyMode.PARALLEL,
        max_parallel_tasks=4,
        batch_size=8,
        timeout_seconds=30,
        retry_attempts=2
    )
)

# Named Configuration Presets
LIC_CONFIG_PRESETS = {
    "development": LICPipelineConfig(
        reasoning_preset=LICReasoningPreset.CONSERVATIVE,
        retrieval_mode=LICRetrievalMode.FAST,
        hyperparameters=LICHyperparameters(
            safety_strictness=LICSafetyStrictness.PERMISSIVE,
            telemetry_enabled=True,
            max_parallel_tasks=2
        ),
        safety_profile=LICSafetyProfile(
            strictness=LICSafetyStrictness.PERMISSIVE,
            enable_pii_detection=False,
            enable_bias_auditing=False,
            enable_content_filtering=True,
            blocked_content_types=["illegal_content"],
            required_approvals=[]
        ),
        concurrency=LICConcurrencyConfig(
            mode=LICConcurrencyMode.SEQUENTIAL,
            max_parallel_tasks=1,
            batch_size=4,
            timeout_seconds=60,
            retry_attempts=3
        ),
        cost_limit_per_run=50.0,
        latency_limit_seconds=60.0,
        enable_telemetry=True
    ),
    
    "production": LICPipelineConfig(
        reasoning_preset=LICReasoningPreset.BALANCED,
        retrieval_mode=LICRetrievalMode.COMPREHENSIVE,
        hyperparameters=LICHyperparameters(
            safety_strictness=LICSafetyStrictness.STRICT,
            cost_limit_per_run=5.0,
            latency_limit_seconds=15.0
        ),
        safety_profile=LICSafetyProfile(
            strictness=LICSafetyStrictness.STRICT,
            enable_pii_detection=True,
            enable_bias_auditing=True,
            enable_content_filtering=True,
            blocked_content_types=["spam", "harassment", "illegal_content", "misinformation"],
            required_approvals=["legal", "compliance"]
        ),
        concurrency=LICConcurrencyConfig(
            mode=LICConcurrencyMode.PARALLEL,
            max_parallel_tasks=6,
            batch_size=12,
            timeout_seconds=15,
            retry_attempts=1
        ),
        cost_limit_per_run=5.0,
        latency_limit_seconds=15.0,
        enable_telemetry=False
    ),
    
    "research": LICPipelineConfig(
        reasoning_preset=LICReasoningPreset.RESEARCH,
        retrieval_mode=LICRetrievalMode.DEEP,
        hyperparameters=LICHyperparameters(
            retrieval_depth=20,
            kg_usage_flags={
                "enable_kg_fallback": True,
                "enable_temporal_kg": True,
                "enable_cross_reference": True,
                "kg_confidence_threshold": "0.5"
            },
            telemetry_enabled=True
        ),
        safety_profile=LICSafetyProfile(
            strictness=LICSafetyStrictness.STANDARD,
            enable_pii_detection=True,
            enable_bias_auditing=True,
            enable_content_filtering=False,
            blocked_content_types=[],
            required_approvals=[]
        ),
        concurrency=LICConcurrencyConfig(
            mode=LICConcurrencyMode.SEQUENTIAL,
            max_parallel_tasks=2,
            batch_size=4,
            timeout_seconds=120,
            retry_attempts=3
        ),
        cost_limit_per_run=100.0,
        latency_limit_seconds=120.0,
        enable_telemetry=True,
        min_confidence_threshold=0.5,
        max_results_per_query=30
    ),
    
    "high_volume": LICPipelineConfig(
        reasoning_preset=LICReasoningPreset.CONSERVATIVE,
        retrieval_mode=LICRetrievalMode.FAST,
        hyperparameters=LICHyperparameters(
            default_reasoning_intensity="low",
            retrieval_depth=5,
            max_parallel_tasks=8
        ),
        safety_profile=LICSafetyProfile(
            strictness=LICSafetyStrictness.STANDARD,
            enable_pii_detection=True,
            enable_bias_auditing=False,
            enable_content_filtering=True,
            blocked_content_types=["spam", "harassment", "illegal_content"],
            required_approvals=[]
        ),
        concurrency=LICConcurrencyConfig(
            mode=LICConcurrencyMode.BATCH,
            max_parallel_tasks=8,
            batch_size=20,
            timeout_seconds=10,
            retry_attempts=1
        ),
        cost_limit_per_run=2.0,
        latency_limit_seconds=10.0,
        enable_telemetry=True,
        min_confidence_threshold=0.8,
        max_results_per_query=5
    )
}


# Configuration Access Functions
def get_lic_pipeline_config(preset_name: Optional[str] = None) -> LICPipelineConfig:
    """Get LIC pipeline configuration by preset name."""
    if preset_name is None:
        return DEFAULT_LIC_CONFIG
    
    return LIC_CONFIG_PRESETS.get(preset_name, DEFAULT_LIC_CONFIG)


def create_custom_lic_config(**kwargs) -> LICPipelineConfig:
    """Create custom LIC pipeline configuration with overrides."""
    # Start with default config and override provided values
    config = LICPipelineConfig(
        reasoning_preset=kwargs.get('reasoning_preset', DEFAULT_LIC_CONFIG.reasoning_preset),
        retrieval_mode=kwargs.get('retrieval_mode', DEFAULT_LIC_CONFIG.retrieval_mode),
        hyperparameters=kwargs.get('hyperparameters', DEFAULT_LIC_CONFIG.hyperparameters),
        safety_profile=kwargs.get('safety_profile', DEFAULT_LIC_CONFIG.safety_profile),
        concurrency=kwargs.get('concurrency', DEFAULT_LIC_CONFIG.concurrency),
        # Feature flags
        enable_company_research=kwargs.get('enable_company_research', DEFAULT_LIC_CONFIG.enable_company_research),
        enable_contact_research=kwargs.get('enable_contact_research', DEFAULT_LIC_CONFIG.enable_contact_research),
        enable_message_generation=kwargs.get('enable_message_generation', DEFAULT_LIC_CONFIG.enable_message_generation),
        enable_rag_enrichment=kwargs.get('enable_rag_enrichment', DEFAULT_LIC_CONFIG.enable_rag_enrichment),
        enable_kg_fallback=kwargs.get('enable_kg_fallback', DEFAULT_LIC_CONFIG.enable_kg_fallback),
        enable_temporal_search=kwargs.get('enable_temporal_search', DEFAULT_LIC_CONFIG.enable_temporal_search),
        # Performance
        cost_limit_per_run=kwargs.get('cost_limit_per_run', DEFAULT_LIC_CONFIG.cost_limit_per_run),
        latency_limit_seconds=kwargs.get('latency_limit_seconds', DEFAULT_LIC_CONFIG.latency_limit_seconds),
        enable_telemetry=kwargs.get('enable_telemetry', DEFAULT_LIC_CONFIG.enable_telemetry),
        # Quality
        min_confidence_threshold=kwargs.get('min_confidence_threshold', DEFAULT_LIC_CONFIG.min_confidence_threshold),
        max_results_per_query=kwargs.get('max_results_per_query', DEFAULT_LIC_CONFIG.max_results_per_query),
        enable_result_deduplication=kwargs.get('enable_result_deduplication', DEFAULT_LIC_CONFIG.enable_result_deduplication)
    )
    
    return config


# Configuration Validation
def validate_lic_config(config: LICPipelineConfig) -> List[str]:
    """Validate LIC pipeline configuration."""
    issues = []
    
    # Check performance limits
    if config.cost_limit_per_run <= 0:
        issues.append("Cost limit per run must be positive")
    
    if config.latency_limit_seconds <= 0:
        issues.append("Latency limit must be positive")
    
    # Check concurrency settings
    if config.concurrency.max_parallel_tasks <= 0:
        issues.append("Max parallel tasks must be positive")
    
    if config.concurrency.batch_size <= 0:
        issues.append("Batch size must be positive")
    
    # Check quality thresholds
    if config.min_confidence_threshold < 0 or config.min_confidence_threshold > 1:
        issues.append("Min confidence threshold must be between 0 and 1")
    
    if config.max_results_per_query <= 0:
        issues.append("Max results per query must be positive")
    
    return issues


# Export constants
__all__ = [
    'LICPipelineConfig',
    'LICReasoningPreset',
    'LICRetrievalMode',
    'LICSafetyProfile',
    'LICConcurrencyConfig',
    'DEFAULT_LIC_CONFIG',
    'LIC_CONFIG_PRESETS',
    'get_lic_pipeline_config',
    'create_custom_lic_config',
    'validate_lic_config'
]
