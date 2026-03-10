"""Runtime Config - Configuration for runtime environment."""

from .shared_infrastructure_config import DomainConfig, SharedInfrastructure, get_shared_infrastructure
from .signal_quality_config import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    ClaimAnalysis,
    QualityThresholds,
    SignalAssessment,
    SignalQuality,
    get_signal_enhancer,
    signal_enhancer,
)

__all__ = [
    "DomainConfig",
    "SharedInfrastructure",
    "get_shared_infrastructure",
    "ClaimAnalysis",
    "QualityThresholds",
    "SignalAssessment",
    "SignalQuality",
    "get_signal_enhancer",
    "signal_enhancer",
]
