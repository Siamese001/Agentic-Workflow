"""
LIC Profile Configuration for Outreach Pipeline

Defines LIC-specific settings and defaults for the outreach workflow.
This is pure configuration - no business logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
from typing import Literal


class LICSafetyStrictness(str, Enum):
    """Safety strictness levels for LIC operations."""
    PERMISSIVE = "permissive"
    STANDARD = "standard"
    STRICT = "strict"


class LICConcurrencyMode(str, Enum):
    """Concurrency modes for LIC operations."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    BATCH = "batch"


@dataclass
class LICHyperparameters:
    """LIC-specific hyperparameters and defaults."""
    
    # LLM Configuration
    default_llm_model: str = "gpt-4"
    temperature_envelope: Dict[str, float] = None
    max_tokens: int = 2048
    
    # Reasoning Configuration
    default_reasoning_intensity: str = "medium"
    retrieval_depth: int = 10
    kg_usage_flags: Dict[str, bool] = None
    
    # Concurrency Settings
    concurrency_mode: LICConcurrencyMode = LICConcurrencyMode.PARALLEL
    max_parallel_tasks: int = 4
    batch_size: int = 8
    
    # Phase 7 Outreach Concurrency Settings
    use_concurrent_research: bool = False
    use_multi_draft: bool = False
    max_parallel_research: int = 2
    max_parallel_drafts: int = 2
    
    # Safety Configuration
    safety_strictness: LICSafetyStrictness = LICSafetyStrictness.STANDARD
    enable_pii_sanitization: bool = True
    enable_bias_auditing: bool = True
    
    # Performance Configuration
    cost_limit_per_run: float = 10.0
    latency_limit_seconds: float = 30.0
    
    # Phase 8 Telemetry Configuration
    telemetry_enabled: bool = True
    telemetry_detail_level: Literal["minimal", "standard", "verbose"] = "standard"
    
    def __post_init__(self):
        """Initialize defaults for complex fields."""
        if self.temperature_envelope is None:
            self.temperature_envelope = {
                "low": 0.3,
                "medium": 0.7,
                "high": 1.0,
                "extreme": 1.2
            }
        
        if self.kg_usage_flags is None:
            self.kg_usage_flags = {
                "enable_kg_fallback": True,
                "enable_temporal_kg": True,
                "enable_cross_reference": True,
                "kg_confidence_threshold": 0.7
            }


# Default LIC Profile Instance
DEFAULT_LIC_PROFILE = LICHyperparameters()


# Profile Override Functions
def get_lic_profile(override_name: Optional[str] = None) -> LICHyperparameters:
    """Get LIC profile with optional override."""
    if override_name is None:
        return DEFAULT_LIC_PROFILE
    
    # Future: Load named profiles from config files
    profiles = {
        "development": LICHyperparameters(
            safety_strictness=LICSafetyStrictness.PERMISSIVE,
            enable_telemetry=True,
            max_parallel_tasks=2
        ),
        "production": LICHyperparameters(
            safety_strictness=LICSafetyStrictness.STRICT,
            cost_limit_per_run=5.0,
            latency_limit_seconds=15.0
        ),
        "research": LICHyperparameters(
            retrieval_depth=20,
            kg_usage_flags={
                "enable_kg_fallback": True,
                "enable_temporal_kg": True,
                "enable_cross_reference": True,
                "kg_confidence_threshold": 0.5
            },
            enable_telemetry=True
        )
    }
    
    return profiles.get(override_name, DEFAULT_LIC_PROFILE)


def create_custom_profile(**kwargs) -> LICHyperparameters:
    """Create a custom LIC profile by overriding defaults."""
    return LICHyperparameters(**kwargs)
