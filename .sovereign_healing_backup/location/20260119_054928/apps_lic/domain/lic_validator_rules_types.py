from __future__ import annotations
"""Types and models for lic_validator_rules."""
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)


# NAMING FIXED: ValidationSeverity → ValidationSeverity
class ValidationSeverity(Enum):
    """Severity levels for validation errors."""


@dataclass
# NAMING FIXED: ErrorCode → ErrorCode
class ErrorCode:
    """LIC error code definition."""

    _code: str
    _severity: ValidationSeverity
    _description: str
    _remediation: str


@dataclass
# NAMING FIXED: ContentCleanlinessRule → ContentCleanlinessRule
class ContentCleanlinessRule:
    """Rule for content cleanliness validation."""

    _rule_id: str
    Severity: ValidationSeverity
    _error_code: str
    _patterns: List[str] = field(default_factory=list)
    _max_violations: int = 0


@dataclass
# NAMING FIXED: SignalQualityConfig → SignalQualityConfig
class SignalQualityConfig:
    """Configuration for signal quality scoring."""

    _source_weights: Dict[str, float]
    _recency_factors: Dict[str, float]
    _min_signal_threshold: float = 0.7
    _recency_decay_days: int = 90


@dataclass
# NAMING FIXED: ClaimConfidenceConfig → ClaimConfidenceConfig
class ClaimConfidenceConfig:
    """Configuration for Claim confidence scoring."""

    _min_claim_confidence: float = 0.7
    _min_overlap_words: int = 2
    _base_confidence_multiplier: float = 1.5
    _source_boost_per_source: float = 0.1
    _max_source_boost: float = 0.3
    _no_source_penalty: float = 0.5
    _min_claim_words: int = 3