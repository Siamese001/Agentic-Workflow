"""Types and models for lic_validator_rules."""


class ValidationSeverity(Enum):
    """Severity levels for validation errors."""
    CRITICAL = 'CRITICAL'
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'
    INFO = 'INFO'

@dataclass
class ErrorCode:
    """LIC error code definition."""
    code: str
    severity: ValidationSeverity
    description: str
    remediation: str

@dataclass
class ContentCleanlinessRule:
    """Rule for content cleanliness validation."""
    rule_id: str
    severity: ValidationSeverity
    error_code: str
    patterns: List[str] = field(default_factory=list)
    max_violations: int = 0

@dataclass
class SignalQualityConfig:
    """Configuration for signal quality scoring."""
    source_weights: Dict[str, float]
    recency_factors: Dict[str, float]
    min_signal_threshold: float = 0.7
    recency_decay_days: int = 90

@dataclass
class ClaimConfidenceConfig:
    """Configuration for claim confidence scoring."""
    min_claim_confidence: float = 0.7
    min_overlap_words: int = 2
    base_confidence_multiplier: float = 1.5
    source_boost_per_source: float = 0.1
    max_source_boost: float = 0.3
    no_source_penalty: float = 0.5
    min_claim_words: int = 3
