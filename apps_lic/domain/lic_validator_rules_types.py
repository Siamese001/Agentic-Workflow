"""Types and models for lic_validator_rules."""
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)


# NAMING FIXED: ValidationSeverity → validation_severity
class validation_severity(Enum):
    """Severity levels for validation errors."""


@dataclass
# NAMING FIXED: ErrorCode → error_code
class error_code:
    """LIC error code definition."""

    _code: str
    _severity: ValidationSeverity
    _description: str
    _remediation: str


@dataclass
# NAMING FIXED: ContentCleanlinessRule → content_cleanliness_rule
class content_cleanliness_rule:
    """Rule for content cleanliness validation."""

    _rule_id: str
    severity: ValidationSeverity
    _error_code: str
    _patterns: List[str] = field(default_factory=list)
    _max_violations: int = 0


@dataclass
# NAMING FIXED: SignalQualityConfig → signal_quality_config
class signal_quality_config:
    """Configuration for signal quality scoring."""

    _source_weights: Dict[str, float]
    _recency_factors: Dict[str, float]
    _min_signal_threshold: float = 0.7
    _recency_decay_days: int = 90


@dataclass
# NAMING FIXED: ClaimConfidenceConfig → claim_confidence_config
class claim_confidence_config:
    """Configuration for claim confidence scoring."""

    _min_claim_confidence: float = 0.7
    _min_overlap_words: int = 2
    _base_confidence_multiplier: float = 1.5
    _source_boost_per_source: float = 0.1
    _max_source_boost: float = 0.3
    _no_source_penalty: float = 0.5
    _min_claim_words: int = 3